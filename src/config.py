"""Configuración global del pipeline de predicción de retornos con LLMs.
Basado en: "Fine-Tuning Large Language Models for Stock Return Prediction Using Newsflow" (EMNLP 2024).
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Any

@dataclass
class ModelConfig:
    # Model backbone: Qwen 3.5 9B oficial
    model_name_or_path: str = "Qwen/Qwen3.5-9B"
    use_qlora: bool = True               # Cuantización a 4-bit (QLoRA) para GPU de 8GB VRAM
    lora_r: int = 16                     # Rango LoRA (r=8 o r=16)
    lora_alpha: int = 32                 # Escala LoRA
    lora_dropout: float = 0.05
    target_modules: Union[List[str], str] = "all-linear"
    pooling_type: str = "aggregated"     # "aggregated" (Mean Pooling Eq. 5) o "bottleneck" (EOS token Eq. 4)
    hidden_dropout: float = 0.1
    num_horizons: int = 3                # 1d, 5d, 20d
    freeze_backbone_epochs: int = 0      # Opcional: congelar backbone al inicio


@dataclass
class DataConfig:
    train_path: str = "data/splits/train/daily_aligned.parquet"
    val_path: str = "data/splits/val/daily_aligned.parquet"
    test_path: str = "data/splits/test/daily_aligned.parquet"
    fundamentals_path: str = "data/fundamentals/quarterly_fundamentals.parquet"
    
    target_return: str = "ret_1d"        # Compatible con pipelines univariados
    target_returns: List[str] = field(default_factory=lambda: ["ret_1d", "ret_5d", "ret_20d"])
    max_token_length: int = 2048         # Longitud máxima de contexto
    include_fundamentals: bool = True    # Inyectar perfil contable SEC EDGAR en el prompt
    filter_news_only: bool = True        # Entrenar solo en días con noticias reportadas


@dataclass
class TrainingConfig:
    output_dir: str = "checkpoints/llm_return_regressor"
    batch_size: int = 4                  # Batch size adaptado a GPU 8GB con grad accumulation
    gradient_accumulation_steps: int = 8 # Batch efectivo = 32 (igual que el paper)
    learning_rate: float = 1e-5          # Tasa de aprendizaje según el paper
    weight_decay: float = 0.01
    warmup_steps: int = 100              # Warmup lineal según el paper
    epochs: int = 5                      # Épocas de entrenamiento
    max_steps: Optional[int] = None      # Límite opcional de pasos (útil para pruebas/pilotos)
    max_hours: Optional[float] = None    # Límite opcional de horas de entrenamiento continuo
    eval_limit: Optional[int] = None     # Límite opcional de muestras a evaluar (útil para pruebas/pilotos ágiles)
    eval_steps: int = 50                 # Evaluar cada N pasos
    save_steps: int = 25                 # Guardar checkpoint periódico cada N pasos
    resume: bool = False                 # Reanudar desde checkpoint previo si existe
    seed: int = 42
    fp16: bool = True
    loss_fn: str = "mse"                 # "mse" o "huber"
