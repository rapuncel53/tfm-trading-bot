"""Módulos y Arquitecturas Multimodales para la predicción de retornos bursátiles.

Basado en:
"Exploring the Synergy of Quantitative Factors and Newsflow Representations from Large Language Models for Stock Return Prediction"
(Tian Guo & Emmanuel Hauptmann, RAM Active Investments, arXiv:2510.15691v3, Nov 2025).

Implementa:
1. FactorsAlone: MLP profunda con skip connections (Apéndice D.3)
2. NewsAlone: Regresión lineal sobre representaciones latentes LLM (Apéndice D.3)
3. FusionCombination: Concatenación + Cuello de Botella (Ecuación 3)
4. FusionSummation: Proyecciones lineales sumadas en espacio latente (Ecuación 4)
5. FusionAttention: Ponderación adaptativa por atención softmax (Ecuaciones 5-6)
6. FININ: Scaled dot-product cross-attention factor-noticia (Wang et al., 2024)
7. MixtureModel: Modelo de mezcla adaptativo (Ecs. 7-8) con Decoupled Training (Ecs. 12-15) y Conventional Training (Ec. 9)
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Tuple, Optional


class FactorsAlone(nn.Module):
    """Componente de predicción basado exclusivamente en factores cuantitativos (Apéndice D.3).
    Arquitectura: Dos capas densas con conexiones residuales (skip connections) y normalización.
    """
    def __init__(self, num_factors: int = 14, hidden_dim: int = 64, num_horizons: int = 3, dropout: float = 0.1):
        super().__init__()
        self.num_horizons = num_horizons
        self.fc1 = nn.Linear(num_factors, hidden_dim)
        self.act = nn.GELU()
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.norm = nn.LayerNorm(hidden_dim)
        self.head = nn.Linear(hidden_dim, num_horizons)

        # Inicialización Xavier
        nn.init.xavier_uniform_(self.fc1.weight)
        nn.init.xavier_uniform_(self.fc2.weight)
        nn.init.xavier_uniform_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def forward(self, x_f: torch.Tensor) -> torch.Tensor:
        # x_f: [batch_size, num_factors]
        h1 = self.dropout(self.act(self.fc1(x_f)))
        h2 = self.norm(h1 + self.dropout(self.fc2(h1)))  # Skip connection
        out = self.head(h2)
        if self.num_horizons == 1:
            return out.squeeze(-1)
        return out


class NewsAlone(nn.Module):
    """Componente de predicción basado exclusivamente en representaciones latentes de noticias del LLM."""
    def __init__(self, news_dim: int = 4096, num_horizons: int = 3, dropout: float = 0.1):
        super().__init__()
        self.num_horizons = num_horizons
        self.norm = nn.LayerNorm(news_dim)
        self.dropout = nn.Dropout(dropout)
        self.head = nn.Linear(news_dim, num_horizons)

        nn.init.xavier_uniform_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def forward(self, x_n: torch.Tensor) -> torch.Tensor:
        # x_n: [batch_size, news_dim]
        h = self.dropout(self.norm(x_n))
        out = self.head(h)
        if self.num_horizons == 1:
            return out.squeeze(-1)
        return out


class FusionCombination(nn.Module):
    """Fusión por Combinación de Representaciones (Ecuación 3 del paper de RAM AI):
    z(x_f, x_n) = h(x_f ⊕ Bottleneck(x_n))
    El paper destaca que esta arquitectura sencilla supera a métodos más complejos.
    """
    def __init__(self, num_factors: int = 14, news_dim: int = 4096, 
                 bottleneck_dim: int = 256, fusion_dim: int = 128, num_horizons: int = 3, dropout: float = 0.1):
        super().__init__()
        self.num_horizons = num_horizons
        # Cuello de botella para reducir la dimensionalidad de las noticias (Apéndice D.3)
        self.news_bottleneck = nn.Sequential(
            nn.LayerNorm(news_dim),
            nn.Dropout(dropout),
            nn.Linear(news_dim, bottleneck_dim),
            nn.GELU()
        )
        # Capa densa de fusión sobre factores concatenados + noticias reducidas
        self.fusion_fc = nn.Sequential(
            nn.Linear(num_factors + bottleneck_dim, fusion_dim),
            nn.LayerNorm(fusion_dim),
            nn.GELU(),
            nn.Dropout(dropout)
        )
        self.head = nn.Linear(fusion_dim, num_horizons)

        nn.init.xavier_uniform_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def forward(self, x_f: torch.Tensor, x_n: torch.Tensor) -> torch.Tensor:
        h_n = self.news_bottleneck(x_n)                  # [batch, bottleneck_dim]
        concat = torch.cat([x_f, h_n], dim=-1)           # [batch, num_factors + bottleneck_dim]
        h_u = self.fusion_fc(concat)                     # [batch, fusion_dim]
        out = self.head(h_u)
        if self.num_horizons == 1:
            return out.squeeze(-1)
        return out


class FusionSummation(nn.Module):
    """Fusión por Suma de Representaciones (Ecuación 4 del paper de RAM AI):
    z(x_f, x_n) = h_f(x_f) + h_n(x_n)
    Proyecta ambas modalidades a un espacio latente común de igual dimensión y las suma.
    """
    def __init__(self, num_factors: int = 14, news_dim: int = 4096, 
                 proj_dim: int = 128, dropout: float = 0.1):
        super().__init__()
        self.proj_f = nn.Sequential(
            nn.Linear(num_factors, proj_dim),
            nn.LayerNorm(proj_dim),
            nn.GELU(),
            nn.Dropout(dropout)
        )
        self.proj_n = nn.Sequential(
            nn.Linear(news_dim, proj_dim),
            nn.LayerNorm(proj_dim),
            nn.GELU(),
            nn.Dropout(dropout)
        )
        self.head = nn.Linear(proj_dim, 1)

        nn.init.xavier_uniform_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def forward(self, x_f: torch.Tensor, x_n: torch.Tensor) -> torch.Tensor:
        hf = self.proj_f(x_f)
        hn = self.proj_n(x_n)
        z = hf + hn
        out = self.head(z).squeeze(-1)
        return out


class FusionAttention(nn.Module):
    """Fusión Atencional Adaptativa (Ecuaciones 5 y 6 del paper de RAM AI):
    z(x_f, x_n) = a_f * h_f(x_f) + a_n * h_n(x_n)
    [a_f, a_n] = softmax(w(x_f, x_n))
    """
    def __init__(self, num_factors: int = 14, news_dim: int = 4096, 
                 proj_dim: int = 128, dropout: float = 0.1):
        super().__init__()
        self.proj_f = nn.Sequential(
            nn.Linear(num_factors, proj_dim),
            nn.LayerNorm(proj_dim),
            nn.GELU()
        )
        self.proj_n = nn.Sequential(
            nn.Linear(news_dim, proj_dim),
            nn.LayerNorm(proj_dim),
            nn.GELU()
        )
        # Gating / logits de atención sobre la combinación de entradas
        self.attn_logits = nn.Sequential(
            nn.Linear(num_factors + proj_dim, 64),
            nn.GELU(),
            nn.Linear(64, 2)
        )
        self.dropout = nn.Dropout(dropout)
        self.head = nn.Linear(proj_dim, 1)

        nn.init.xavier_uniform_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def forward(self, x_f: torch.Tensor, x_n: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        hf = self.proj_f(x_f)
        hn = self.proj_n(x_n)

        # Calcular pesos de atención [a_f, a_n]
        logits = self.attn_logits(torch.cat([x_f, hn], dim=-1))
        weights = F.softmax(logits, dim=-1)  # [batch, 2]
        af = weights[:, 0:1]
        an = weights[:, 1:2]

        z = self.dropout(af * hf + an * hn)
        out = self.head(z).squeeze(-1)
        return out, weights


class FININ(nn.Module):
    """Línea base FININ (Wang et al., 2024 / RAM AI Baseline, Apéndice D.3):
    Scaled dot-product attention entre factores y noticias para modular la representación textual.
    """
    def __init__(self, num_factors: int = 14, news_dim: int = 4096, 
                 proj_dim: int = 128, dropout: float = 0.1):
        super().__init__()
        self.proj_f = nn.Linear(num_factors, proj_dim)
        self.proj_n = nn.Linear(news_dim, proj_dim)
        self.scale = math.sqrt(proj_dim)
        self.head = nn.Linear(proj_dim, 1)

    def forward(self, x_f: torch.Tensor, x_n: torch.Tensor) -> torch.Tensor:
        hf = self.proj_f(x_f)
        hn = self.proj_n(x_n)
        # Scaled dot-product scalar weight
        dot_score = torch.sum(hf * hn, dim=-1, keepdim=True) / self.scale
        weight = torch.sigmoid(dot_score)
        z = hf + weight * hn
        out = self.head(z).squeeze(-1)
        return out


class MixtureModel(nn.Module):
    """Modelo de Mezcla de Expertos Multimodal (Ecs. 7-8 del paper de RAM AI):
    r̂ = p_f(x_f, x_n) * g_f(x_f) + p_u(x_f, x_n) * g_u(x_u)

    Soporta:
    1. Conventional Training: Optimización conjunta de MSE (Ec. 9).
    2. Decoupled Training (RAM AI): Entrenamiento desacoplado e independiente de componentes (Ec. 13)
       + Distribution Matching vía divergencia KL contra el posterior óptimo analítico (Ec. 14-15).
    """
    def __init__(self, num_factors: int = 14, news_dim: int = 4096,
                 bottleneck_dim: int = 256, fusion_dim: int = 128, 
                 temperature: float = 1.0):
        super().__init__()
        self.temperature = temperature
        
        # Componente 1: Factors Alone g_θf(x_f)
        self.factors_component = FactorsAlone(num_factors=num_factors, hidden_dim=64)
        
        # Componente 2: Fusion Combination g_θu(x_u)
        self.fusion_component = FusionCombination(
            num_factors=num_factors, 
            news_dim=news_dim, 
            bottleneck_dim=bottleneck_dim, 
            fusion_dim=fusion_dim
        )
        
        # Red de Gating p_ϕ(I | x_f, x_n) (Ecuación 8)
        self.gating = nn.Sequential(
            nn.Linear(num_factors + bottleneck_dim, 64),
            nn.GELU(),
            nn.Linear(64, 2)
        )

    def forward(self, x_f: torch.Tensor, x_n: torch.Tensor) -> Dict[str, torch.Tensor]:
        # Predicción de cada componente
        pred_f = self.factors_component(x_f)
        pred_u = self.fusion_component(x_f, x_n)

        # Representación reducida de noticias para el gating
        with torch.no_grad():
            h_n = self.fusion_component.news_bottleneck(x_n)
        
        gating_input = torch.cat([x_f, h_n], dim=-1)
        logits = self.gating(gating_input)
        probs = F.softmax(logits, dim=-1)  # [batch, 2]: (p_f, p_u)
        p_f = probs[:, 0]
        p_u = probs[:, 1]

        # Predicción combinada
        pred_mix = p_f * pred_f + p_u * pred_u

        return {
            'pred_mix': pred_mix,
            'pred_f': pred_f,
            'pred_u': pred_u,
            'probs': probs,
            'p_f': p_f,
            'p_u': p_u
        }

    def compute_decoupled_loss(self, x_f: torch.Tensor, x_n: torch.Tensor, 
                               targets: torch.Tensor, lambda_kl: float = 1.0) -> Dict[str, torch.Tensor]:
        """Calcula la pérdida desacoplada (Ecuaciones 12–15 del paper de RAM AI).
        L_total = L_independent(θ_f, θ_u) + λ * L_distribution_matching(ϕ)
        """
        outputs = self.forward(x_f, x_n)
        pred_f = outputs['pred_f']
        pred_u = outputs['pred_u']
        probs = outputs['probs']

        # 1. Independent Training Loss (Ecuación 13):
        # Entrena cada componente para minimizar su propio error cuadrático de forma independiente
        loss_f = F.mse_loss(pred_f, targets)
        loss_u = F.mse_loss(pred_u, targets)
        loss_independent = loss_f + loss_u

        # 2. Target Posterior Distribution (Ecuación 15):
        # P(I=f) = softmax( -(r - r̂_f)^2 / τ , -(r - r̂_u)^2 / τ )
        with torch.no_grad():
            err_f = (targets - pred_f) ** 2
            err_u = (targets - pred_u) ** 2
            target_logits = torch.stack([-err_f / self.temperature, -err_u / self.temperature], dim=-1)
            target_probs = F.softmax(target_logits, dim=-1)  # [batch, 2]

        # 3. Distribution Matching vía KL Divergence (Ecuación 14):
        # KL(p_ϕ || p_target) = sum( p_ϕ * (log(p_ϕ) - log(p_target)) )
        log_probs = F.log_softmax(self.gating(torch.cat([x_f, self.fusion_component.news_bottleneck(x_n).detach()], dim=-1)), dim=-1)
        loss_kl = F.kl_div(log_probs, target_probs, reduction='batchmean')

        # Pérdida total desacoplada
        loss_total = loss_independent + lambda_kl * loss_kl

        return {
            'loss_total': loss_total,
            'loss_independent': loss_independent,
            'loss_f': loss_f,
            'loss_u': loss_u,
            'loss_kl': loss_kl,
            'outputs': outputs,
            'target_probs': target_probs
        }
