import json
from typing import Any, Dict, Tuple

import numpy as np
import pytorch_lightning as pl
import torch
from torch.utils.data import DataLoader
from torch.utils.data import Dataset as Dataset_

from models.intrinsic_curiosity_module import IntrinsicCuriosityModule
from models.parking_sensor_network.model import MultimodalEncoder


class Dataset(Dataset_):
    def __init__(self, split: str = "train"):  ## train or val
        self.split = split
        with open("/home/cherniak/Self-driving-RL-car/steering_data.json") as f:
            data = json.load(f)
        if split == "train":
            self.data = data[: int(len(data) * 0.85)]
        elif split == "val":
            self.data = data[int(len(data) * 0.85): ]

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index) -> Tuple[Dict[str, Any], Dict[str, Any], float]:
        sample = self.data[index]
        observation_before = {k: np.array(v).astype(np.float32) for k, v in sample["observation_before"].items()}
        observation_before["steering"] = observation_before["steering"].reshape(1,)
        observation_after = {k: np.array(v).astype(np.float32) for k, v in sample["observation_after"].items()}
        observation_after["steering"] = observation_after["steering"].reshape(1,)
        action = np.array(sample["action"]).astype(np.float32).reshape(1,)
        return observation_before, observation_after, action

class LightningModule(pl.LightningModule):
    def __init__(self):
        super().__init__()
        encoder = MultimodalEncoder()

        forward_dynamics_model_kwargs = {"embedding_dim": encoder.out_features}
        inverse_dynamics_model_kwargs = {"embedding_dim": encoder.out_features}

        self.icm = IntrinsicCuriosityModule(
            encoder,
            forward_dynamics_model_kwargs,
            inverse_dynamics_model_kwargs,
        )

    def training_step(self, batch, batch_idx) -> torch.Tensor:
        observation_before, observation_after, action = batch
        loss, forward_dynamics_loss, inverse_dynamics_loss = self.icm.loss(observation_before, observation_after, action)
        self.log("train/loss", loss)
        self.log("train/forward_dynamics_loss", forward_dynamics_loss)
        self.log("train/inverse_dynamics_loss", inverse_dynamics_loss)
        return loss

    def validation_step(self, batch, batch_idx) -> torch.Tensor:
        observation_before, observation_after, action = batch
        with torch.no_grad():
            loss, forward_dynamics_loss, inverse_dynamics_loss = self.icm.loss(observation_before, observation_after, action)
        self.log("val/loss", loss)
        self.log("val/forward_dynamics_loss", forward_dynamics_loss)
        self.log("val/inverse_dynamics_loss", inverse_dynamics_loss)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=1e-4)
        return optimizer

def pretrain_parking_sensor_encoder_with_icm():
    model = LightningModule()
    train_dataset = Dataset(split="train")
    val_dataset = Dataset(split="val")
    train_dataloader = DataLoader(train_dataset, batch_size=1024, num_workers=4)
    val_dataloader = DataLoader(val_dataset, batch_size=1024, num_workers=4)

    trainer = pl.Trainer(
        # auto_scale_batch_size=True,
        # auto_lr_find=True,
        max_epochs=50,
        enable_checkpointing=True,
        check_val_every_n_epoch=1,
        log_every_n_steps=50,
        accelerator="cpu",
        logger=pl.loggers.TensorBoardLogger("/home/cherniak/Self-driving-RL-car/logs/pretrain_parking_sensor_encoder_with_icm"),
    )

    trainer.fit(model, train_dataloader, val_dataloader)
