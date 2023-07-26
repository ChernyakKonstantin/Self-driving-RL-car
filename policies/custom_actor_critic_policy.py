from typing import Callable
from gymnasium import spaces
from torch import nn

from stable_baselines3.common.policies import ActorCriticPolicy


class CustomActorCriticPolicy(ActorCriticPolicy):
    def __init__(
        self,
        observation_space: spaces.Space,
        action_space: spaces.Space,
        lr_schedule: Callable[[float], float],
        custom_network_builder: Callable = None,
        *args,
        **kwargs,
    ):
        self.custom_network_builder = custom_network_builder
        assert custom_network_builder is not None, "custom_network_builder is required"
        # Disable orthogonal initialization
        kwargs["ortho_init"] = False
        super().__init__(
            observation_space,
            action_space,
            lr_schedule,
            # Pass remaining arguments to base class
            *args,
            **kwargs,
        )

    def _build_mlp_extractor(self) -> None:
        self.mlp_extractor = self.custom_network_builder()