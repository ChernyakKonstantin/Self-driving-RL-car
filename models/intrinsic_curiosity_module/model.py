import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Any

class InverseDynamicsModel(nn.Module):
    def __init__(
            self,
            embedding_dim: int,
            action_dim: int = 1,
            n_layers: int = 1,
            hidden_dim: int = 128,
            action_type: str = "continuous", # `continuous` or `discrete`
            ):
        super().__init__()
        assert n_layers >= 1, "n_layers must be at least 1"
        assert action_type in ["continuous", "discrete"], "action_type must be `continuous` or `discrete`"

        self.action_type = action_type

        self.model = nn.Sequential()
        self.model.extend(self._build_block(embedding_dim * 2, hidden_dim))
        for _ in range(n_layers):
            self.model.extend(self._build_block(hidden_dim, hidden_dim))
        if self.action_type == "continuous":
            self.model.append(nn.Linear(hidden_dim, action_dim))
        elif self.action_type == "discrete":
            raise NotImplementedError("Discrete action is not supported yet.")  # TODO

    def _build_block(self, in_features: int, out_features: int) -> List[nn.Module]:
        return [
            nn.Linear(in_features, out_features),
            nn.BatchNorm1d(out_features),
            nn.ReLU(),
        ]

    def forward(self, embedding_before: torch.Tensor, embedding_after: torch.Tensor) -> torch.Tensor:
        x = torch.cat([embedding_before, embedding_after], dim=1)
        return self.model(x)

    def loss(self, y_pred: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        if self.action_type == "continuous":
            return F.mse_loss(y_pred, y)
        elif self.action_type == "discrete":
            raise NotImplementedError("Discrete action is not supported yet.")  # TODO

class ForwardDynamicsModel(nn.Module):
    def __init__(
            self,
            embedding_dim: int,
            action_dim: int = 1,
            n_layers: int = 2,
            hidden_dim: int = 128,
        ):
        super().__init__()
        self.model = nn.Sequential()
        self.model.extend(self._build_block(embedding_dim + action_dim, hidden_dim))
        for _ in range(n_layers):
            self.model.extend(self._build_block(hidden_dim, hidden_dim))
        self.model.append(nn.Linear(hidden_dim, embedding_dim))

    def _build_block(self, in_features: int, out_features: int) -> List[nn.Module]:
        return [
            nn.Linear(in_features, out_features),
            nn.BatchNorm1d(out_features),
            nn.ReLU(),
        ]

    def forward(self, embedding: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        x = torch.cat([embedding, action], dim=1)
        return self.model(x)

    def loss(self, y_pred: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        return F.mse_loss(y_pred, y)

class IntrinsicCuriosityModule(nn.Module):
    def __init__(
            self,
            encoder: nn.Module,
            forward_dynamics_model_kwargs: Dict[str, Any],
            inverse_dynamics_model_kwargs: Dict[str, Any],
            lambda_f: float = 1.0,
            lambda_i: float = 1.0,
        ):
        super().__init__()
        self.encoder = encoder
        self.lambda_f = lambda_f
        self.lambda_i = lambda_i
        self.forward_dynamics_model = ForwardDynamicsModel(**forward_dynamics_model_kwargs)
        self.inverse_dynamics_model = InverseDynamicsModel(**inverse_dynamics_model_kwargs)

    def loss(self, observation_before: Any, observation_after: Any, action: torch.Tensor) -> torch.Tensor:
        embedding_before = self.encoder(observation_before)
        embedding_after = self.encoder(observation_after)

        embedding_after_pred = self.forward_dynamics_model(embedding_before, action)
        action_pred = self.inverse_dynamics_model(embedding_before, embedding_after)

        forward_dynamics_loss = self.forward_dynamics_model.loss(embedding_after_pred, embedding_after)
        inverse_dynamics_loss = self.inverse_dynamics_model.loss(action_pred, action)
        return forward_dynamics_loss * self.lambda_f + inverse_dynamics_loss * self.lambda_i, forward_dynamics_loss, inverse_dynamics_loss
