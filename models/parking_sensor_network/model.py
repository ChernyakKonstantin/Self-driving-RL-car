from typing import Tuple, Dict
import gymnasium as gym
import torch
import torch.nn as nn
import torch.nn.functional as F
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class ParkingSensorEncoder(nn.Module):
    def __init__(
            self,
            in_features: int = 1,
            sequence_len: int = 4,
            encoder_hidden_dim: int = 16,
            transformer_hidden_dim: int = 64,
            transformer_nhead: int = 1,
        ):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Flatten(start_dim=2),
            nn.Linear(in_features * sequence_len, encoder_hidden_dim),
            nn.ReLU(),
            nn.Linear(encoder_hidden_dim, encoder_hidden_dim),
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

class ParkingSensorNetwork(nn.Module):
    def __init__(
            self,
            parking_sensor_in_features: int = 1,
            other_in_features: int = 1,
            sequence_len: int = 4,
            parking_sensor_encoder_hidden_dim: int = 16,
            parking_sensor_transformer_hidden_dim: int = 64,
            parking_sensor_transformer_nhead: int = 1,
            shared_network_hidden_dim: int = 32,
            last_layer_dim_pi: int = 16,
            last_layer_dim_vf: int = 16,
    ):
        super().__init__()

        # Save dim, used to create the distributions
        self.latent_dim_pi = last_layer_dim_pi
        self.latent_dim_vf = last_layer_dim_vf

        self.parking_sensor_encoder = ParkingSensorEncoder(
            parking_sensor_in_features,
            sequence_len,
            parking_sensor_encoder_hidden_dim,
            parking_sensor_transformer_hidden_dim,
            parking_sensor_transformer_nhead,
        )

        self.shared_network = nn.Sequential(
            nn.Linear(parking_sensor_encoder_hidden_dim + other_in_features,  shared_network_hidden_dim),
            nn.ReLU(),
            nn.Linear(shared_network_hidden_dim,  shared_network_hidden_dim),
            nn.ReLU(),
            nn.Linear(shared_network_hidden_dim,  shared_network_hidden_dim),
            nn.ReLU(),
        )

        self.policy_net = nn.Sequential(
            nn.Linear(shared_network_hidden_dim, last_layer_dim_pi),
            nn.ReLU()
        )

        self.value_net = nn.Sequential(
            nn.Linear(shared_network_hidden_dim, last_layer_dim_vf),
            nn.ReLU()
        )

    def forward(self, x: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        :return: (torch.Tensor, torch.Tensor) latent_policy, latent_value of the specified network.
            If all layers are shared, then ``latent_policy == latent_value``
        """
        # Shape: [batch_size, shared_network_hidden_dim]
        features = self.forward_shared(x)
        # Shape: [batch_size, last_layer_dim_pi], [batch_size, last_layer_dim_vf]
        return self.policy_net(features), self.value_net(features)

    def forward_shared(self, x: Dict[str, torch.Tensor]) -> torch.Tensor:
        # Shape: [batch_size, n_sensors, action_repeat, feature_dim]
        parking_sensor = x["parking_sensor"]
        # Shape: [batch_size, feature_dim]. It is steering and etc.
        other = x["other"]
        # Shape: [batch_size, parking_sensor_transformer_hidden_dim]
        parking_sensor_features = self.parking_sensor_encoder(parking_sensor)
        # Shape: [batch_size, parking_sensor_transformer_hidden_dim + other_in_features]
        joined_data = torch.cat([parking_sensor_features, other], dim=1)
        # Shape: [batch_size, shared_network_hidden_dim]
        return self.shared_network(joined_data)

    def forward_actor(self, x: Dict[str, torch.Tensor]) -> torch.Tensor:
        features = self.forward_shared(x)
        return self.policy_net(features)

    def forward_critic(self, x: Dict[str, torch.Tensor]) -> torch.Tensor:
        features = self.forward_shared(x)
        return self.value_net(features)

class ParkingSensorExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Dict):
        # We do not know features-dim here before going over all the items,
        # so put something dummy for now. PyTorch requires calling
        # nn.Module.__init__ before adding modules
        super().__init__(observation_space, features_dim=1)

        self.key_order = None

    def forward(self, observations) -> Dict[str, torch.Tensor]:
        x = {}
        if self.key_order is None:
            self.key_order = list(observations.keys())

        for key in self.key_order:
            if key == "parking_sensor":
                x[key] = observations[key]
            else:
                if "other" not in x:
                    x["other"] = []
                x["other"].append(observations[key])
        x["other"] = torch.cat(x["other"], dim=1)
        return x