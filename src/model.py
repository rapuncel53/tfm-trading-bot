"""Arquitectura PyTorch del modelo LLMReturnRegressor.

Implementa estrictamente la formulación de:
"Fine-Tuning Large Language Models for Stock Return Prediction Using Newsflow" (EMNLP 2024, RAM Active Investments).

Ecuación 1:
    r̂_{s, t+ℓ} = f ∘ g(X_{s, <t})

Ecuación 5 (Aggregated Representation / Mean Pooling de Tokens):
    r̂_{s, t+ℓ} = f( (1 / L) ∑_{l=1}^L h_l )
"""

import os
from typing import Optional, Tuple, Dict, Any

try:
    import torch
    import torch.nn as nn
    from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
except ImportError:
    # Definiciones de fallback si se ejecuta en entorno sin torch instalado
    class nn:
        class Module:
            pass

from src.config import ModelConfig


class MaskedMeanPooling(nn.Module):
    """Implementa la Ecuación 5 del paper: promediado ponderado de tokens por attention_mask."""

    def __init__(self):
        super().__init__()

    def forward(self, hidden_states: "torch.Tensor", attention_mask: "torch.Tensor") -> "torch.Tensor":
        # hidden_states: [batch_size, seq_len, hidden_dim]
        # attention_mask: [batch_size, seq_len]
        mask_expanded = attention_mask.unsqueeze(-1).expand_as(hidden_states).float()
        sum_embeddings = torch.sum(hidden_states * mask_expanded, dim=1)
        sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
        return sum_embeddings / sum_mask  # [batch_size, hidden_dim]


class MultiHorizonLoss(nn.Module):
    """Calcula el MSE multi-horizonte ponderado por la varianza empírica de cada horizonte.
    Evita que el horizonte más volátil (20d, std ~7.9%) ahogue el gradiente de 1d (std ~2.2%).
    """
    def __init__(self, stds: Optional[list] = None):
        super().__init__()
        if stds is None:
            stds = [0.0225, 0.0433, 0.0789]
        inv_vars = [1.0 / (s ** 2) for s in stds]
        tot = sum(inv_vars)
        w = [v / tot * len(stds) for v in inv_vars]
        self.register_buffer("weights", torch.tensor(w, dtype=torch.float32))

    def forward(self, preds: "torch.Tensor", targets: "torch.Tensor") -> "torch.Tensor":
        diff = preds - targets
        w = self.weights.to(preds.device)
        if preds.dim() == 2 and targets.dim() == 2:
            weighted_diff2 = (diff ** 2) * w.unsqueeze(0)
            return torch.mean(weighted_diff2)
        return torch.mean(diff ** 2)


class ForecastingHead(nn.Module):
    """Capa densa de pronóstico de retorno f(h) -> r̂ ∈ ℝ^K (1d, 5d, 20d)."""

    def __init__(self, hidden_dim: int, num_horizons: int = 1, dropout: float = 0.1):
        super().__init__()
        self.num_horizons = num_horizons
        self.layer_norm = nn.LayerNorm(hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(hidden_dim, num_horizons)

        # Inicialización de pesos para regresión centrada en 0
        nn.init.xavier_uniform_(self.linear.weight)
        nn.init.zeros_(self.linear.bias)

    def forward(self, h: "torch.Tensor") -> "torch.Tensor":
        x = self.layer_norm(h)
        x = self.dropout(x)
        out = self.linear(x)  # [batch_size, num_horizons]
        if self.num_horizons == 1:
            return out.squeeze(-1)
        return out


class LLMReturnRegressor(nn.Module):
    """Modelo completo News-to-Return que combina Backbone LLM + Mean Pooling (Eq. 5) + Forecasting Head."""

    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        
        # 1. Configurar Quantización para GPU (QLoRA 4-bit) si está habilitada
        bnb_config = None
        if config.use_qlora:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True
            )

        print(f"[Model] Cargando backbone LLM: {config.model_name_or_path} (QLoRA={config.use_qlora})...")
        self.backbone = AutoModel.from_pretrained(
            config.model_name_or_path,
            quantization_config=bnb_config,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True
        )

        # Obtener dimensión oculta (compatible con arquitecturas estándar y Qwen3.5)
        hidden_dim = getattr(self.backbone.config, 'hidden_size', None)
        if hidden_dim is None and hasattr(self.backbone.config, 'text_config'):
            hidden_dim = getattr(self.backbone.config.text_config, 'hidden_size', None)
        if hidden_dim is None:
            hidden_dim = 4096
        print(f"[Model] Dimensión oculta del backbone (D): {hidden_dim}")

        # 2. Configurar Adaptadores LoRA
        if config.use_qlora:
            self.backbone = prepare_model_for_kbit_training(self.backbone)

        lora_config = LoraConfig(
            r=config.lora_r,
            lora_alpha=config.lora_alpha,
            lora_dropout=config.lora_dropout,
            target_modules=config.target_modules,
            bias="none",
            task_type=TaskType.FEATURE_EXTRACTION
        )
        self.backbone = get_peft_model(self.backbone, lora_config)
        self.backbone.print_trainable_parameters()

        # 3. Módulo de Agregación de Tokens (Ecuación 5 del paper)
        self.pooling = MaskedMeanPooling()

        # 4. Cabezal de Regresión f(h) (Soporta 1d, 5d, 20d)
        num_horizons = getattr(config, 'num_horizons', 1)
        self.forecasting_head = ForecastingHead(hidden_dim, num_horizons=num_horizons, dropout=config.hidden_dropout)
        if torch.cuda.is_available():
            self.forecasting_head = self.forecasting_head.cuda()

        # 5. Función de pérdida (MSE univariado o MultiHorizonLoss)
        if num_horizons > 1:
            self.loss_fn = MultiHorizonLoss()
        else:
            self.loss_fn = nn.MSELoss()

    def forward(self, input_ids: "torch.Tensor", attention_mask: "torch.Tensor", 
                targets: Optional["torch.Tensor"] = None) -> Dict[str, "torch.Tensor"]:
        # Pasar por el backbone LLM (Feature Extractor)
        outputs = self.backbone(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        if hasattr(outputs, 'last_hidden_state') and outputs.last_hidden_state is not None:
            last_hidden_state = outputs.last_hidden_state
        elif hasattr(outputs, 'hidden_states') and outputs.hidden_states is not None:
            last_hidden_state = outputs.hidden_states[-1]
        else:
            last_hidden_state = outputs[0]

        # Promediado de representaciones de tokens (Ecuación 5)
        if self.config.pooling_type == "aggregated":
            h_pooled = self.pooling(last_hidden_state, attention_mask)
        else:
            # Bottleneck (último token real según attention_mask)
            seq_lens = attention_mask.sum(dim=1).long() - 1
            batch_indices = torch.arange(last_hidden_state.size(0), device=last_hidden_state.device)
            h_pooled = last_hidden_state[batch_indices, seq_lens]

        # Asegurar tipo y dispositivo compatibles con la cabeza de regresión
        head_device = next(self.forecasting_head.parameters()).device
        h_pooled = h_pooled.to(device=head_device, dtype=torch.float32)

        # Predecir retorno continuo r̂
        preds = self.forecasting_head(h_pooled)

        loss = None
        if targets is not None:
            loss = self.loss_fn(preds, targets.to(head_device).float())

        return {
            'preds': preds,
            'loss': loss,
            'pooled_embeddings': h_pooled
        }
