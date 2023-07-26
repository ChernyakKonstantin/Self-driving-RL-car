from typing import Dict, Tuple

import gymnasium as gym
import torch
import torch.nn as nn
import torch.nn.functional as F
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor


class ParkingSensorsBatchNorm1d(nn.BatchNorm1d):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, n_features = x.shape
        x = x.reshape(batch_size, seq_len * n_features)
        x = super().forward(x)
        x = x.reshape(batch_size, seq_len, n_features)
        return x

class ParkingSensorEncoder(nn.Module):
    def __init__(
            self,
            in_features: int = 1,
            n_sensors: int = 8,
            sequence_len: int = 4,
            encoder_hidden_dim: int = 16,
            transformer_hidden_dim: int = 64,
            transformer_nhead: int = 1,
        ):
        super().__init__()
        self.out_features = encoder_hidden_dim
        self.encoder = nn.Sequential(
            nn.Flatten(start_dim=2),
            nn.Linear(in_features * sequence_len, encoder_hidden_dim),
            ParkingSensorsBatchNorm1d(n_sensors * encoder_hidden_dim),
            nn.ReLU(),
            nn.Linear(encoder_hidden_dim, encoder_hidden_dim),
            ParkingSensorsBatchNorm1d(n_sensors * encoder_hidden_dim),
            nn.ReLU(),
        )
        self.transformer = nn.TransformerEncoderLayer(
            encoder_hidden_dim,
            nhead=transformer_nhead,
            dim_feedforward=transformer_hidden_dim,
        )
        self.aggregator = nn.Parameter(torch.randn(1, 1, encoder_hidden_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x shape is [batch_size, n_sensors, action_repeat, feature_dim]."""
        # Shape: [batch_size, n_sensors, encoder_hidden_dim]
        x = self.encoder(x)
        # Shape: [batch_size, 1 + n_sensors, encoder_hidden_dim]
        x = torch.concat([self.aggregator.expand(x.shape[0], -1, -1), x, ], dim=1)
        # Shape: [batch_size, 1 + n_sensors, transformer_hidden_dim]
        x = self.transformer(x)
        # Shape: [batch_size, transformer_hidden_dim]
        return x[:, 0, :].squeeze(1)

class MultimodalEncoder(nn.Module):
    def __init__(
            self,
            parking_sensor_in_features: int = 1,
            steering_in_features: int = 1,
            n_sensors = 8,
            sequence_len: int = 4,
            parking_sensor_encoder_hidden_dim: int = 16,
            parking_sensor_transformer_hidden_dim: int = 64,
            parking_sensor_transformer_nhead: int = 1,
            steering_encoder_hidden_dim: int = 2,
            shared_network_hidden_dim: int = 8,
    ) -> None:
        super().__init__()
        self.out_features = shared_network_hidden_dim
        self.parking_sensor_encoder = ParkingSensorEncoder(
            parking_sensor_in_features,
            n_sensors,
            sequence_len,
            parking_sensor_encoder_hidden_dim,
            parking_sensor_transformer_hidden_dim,
            parking_sensor_transformer_nhead,
        )
        self.steering_encoder = nn.Sequential(
            nn.Linear(steering_in_features, steering_encoder_hidden_dim),
            nn.BatchNorm1d(steering_encoder_hidden_dim),
            nn.ReLU(),
        )
        self.shared_network = nn.Sequential(
            nn.Linear(self.parking_sensor_encoder.out_features  + steering_encoder_hidden_dim,  shared_network_hidden_dim),
            nn.BatchNorm1d(shared_network_hidden_dim),
            nn.ReLU(),
            nn.Linear(shared_network_hidden_dim, shared_network_hidden_dim),
            nn.BatchNorm1d(shared_network_hidden_dim),
            nn.ReLU(),
        )

    def forward(self, x: Dict[str, torch.Tensor]) -> torch.Tensor:
        # Shape: [batch_size, n_sensors, action_repeat, feature_dim]
        parking_sensor = x["parking_sensor"]
        # Shape: [batch_size, feature_dim]. It is steering and etc.
        steering = x["steering"]
        # Shape: [batch_size, parking_sensor_transformer_hidden_dim]
        parking_sensor_features = self.parking_sensor_encoder(parking_sensor)
        # Shape: [batch_size, steering_encoder_hidden_dim]
        steering_features = self.steering_encoder(steering)
        # Shape: [batch_size, parking_sensor_transformer_hidden_dim + steering_encoder_hidden_dim]
        joined_data = torch.cat([parking_sensor_features, steering_features], dim=1)
        # Shape: [batch_size, shared_network_hidden_dim]
        return self.shared_network(joined_data)

class ParkingSensorNetwork(nn.Module):
    def __init__(
            self,
            parking_sensor_in_features: int = 1,
            steering_in_features: int = 1,
            n_sensors: int = 8,
            sequence_len: int = 4,
            parking_sensor_encoder_hidden_dim: int = 16,
            parking_sensor_transformer_hidden_dim: int = 64,
            parking_sensor_transformer_nhead: int = 1,
            steering_encoder_hidden_dim: int = 2,
            shared_network_hidden_dim: int = 32,
            last_layer_dim_pi: int = 16,
            last_layer_dim_vf: int = 16,
    ):
        super().__init__()

        # Save dim, used to create the distributions
        self.latent_dim_pi = last_layer_dim_pi
        self.latent_dim_vf = last_layer_dim_vf

        self.encoder = MultimodalEncoder(
            parking_sensor_in_features,
            steering_in_features,
            n_sensors,
            sequence_len,
            parking_sensor_encoder_hidden_dim,
            parking_sensor_transformer_hidden_dim,
            parking_sensor_transformer_nhead,
            steering_encoder_hidden_dim,
            shared_network_hidden_dim,
        )

        self.policy_net = nn.Sequential(
            nn.Linear(self.encoder.out_features, last_layer_dim_pi),
            nn.ReLU(),
        )

        self.value_net = nn.Sequential(
            nn.Linear(self.encoder.out_features, last_layer_dim_vf),
            nn.ReLU(),
        )

    def forward(self, x: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        :return: (torch.Tensor, torch.Tensor) latent_policy, latent_value of the specified network.
            If all layers are shared, then ``latent_policy == latent_value``
        """
        # Shape: [batch_size, shared_network_hidden_dim]
        features = self.encoder(x)
        # Shape: [batch_size, last_layer_dim_pi], [batch_size, last_layer_dim_vf]
        return self.policy_net(features), self.value_net(features)

    def forward_actor(self, x: Dict[str, torch.Tensor]) -> torch.Tensor:
        features = self.encoder(x)
        return self.policy_net(features)

    def forward_critic(self, x: Dict[str, torch.Tensor]) -> torch.Tensor:
        features = self.encoder(x)
        return self.value_net(features)

class ParkingSensorExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Dict):
        # We do not know features-dim here before going over all the items,
        # so put something dummy for now. PyTorch requires calling
        # nn.Module.__init__ before adding modules
        super().__init__(observation_space, features_dim=1)

        self.key_order = None

    def forward(self, observations: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        return observations