# Improving k-Means Clustering Performance with Disentangled Internal Representations
# Copyright (C) 2020  Abien Fred Agarap
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""PyTorch implementation of a vanilla Autoencoder"""
import torch
import torch.nn as nn


class Autoencoder(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        self.encoder_layers = torch.nn.ModuleList([
            torch.nn.Linear(in_features=kwargs["input_shape"], out_features=500),
            torch.nn.ReLU(),
            torch.nn.Linear(in_features=500, out_features=500),
            torch.nn.ReLU(),
            torch.nn.Linear(in_features=500, out_features=2000),
            torch.nn.ReLU(),
            torch.nn.Linear(in_features=2000, out_features=kwargs["code_dim"]),
            torch.nn.Sigmoid()
        ])
        self.decoder_layers = torch.nn.ModuleList([
            torch.nn.Linear(in_features=kwargs["code_dim"], out_features=2000),
            torch.nn.ReLU(),
            torch.nn.Linear(in_features=2000, out_features=500),
            torch.nn.ReLU(),
            torch.nn.Linear(in_features=500, out_features=500),
            torch.nn.ReLU(),
            torch.nn.Linear(in_features=500, out_features=kwargs["input_shape"]),
            torch.nn.Sigmoid()
        ])

    def forward(self, features):
        activation = self.enc_hidden_layer_1(features)
        activation = torch.relu(activation)
        activation = self.enc_hidden_layer_2(activation)
        activation = torch.relu(activation)
        activation = self.enc_hidden_layer_3(activation)
        activation = torch.relu(activation)
        activation = self.code_layer(activation)
        code = torch.sigmoid(activation)

        activation = self.dec_hidden_layer_1(code)
        activation = torch.relu(activation)
        activation = self.dec_hidden_layer_2(activation)
        activation = torch.relu(activation)
        activation = self.dec_hidden_layer_3(activation)
        activation = torch.relu(activation)
        activation = self.reconstruction_layer(activation)
        reconstruction = torch.sigmoid(activation)
        return reconstruction


def train_step(
    model: nn.Module, optimizer: object, features: torch.Tensor, loss_fn: object
) -> torch.Tensor:
    """
    Trains a model for a single step.

    Parameters
    ----------
    model : nn.Module
        The model to train.
    optimizer : object
        The optimizer function to use.
    features : torch.Tensor
        The features to train on.
    loss_fn : object
        The loss function to optimize.

    Returns
    -------
    train_loss : torch.Tensor
        The training loss for a single step.
    """
    optimizer.zero_grad()
    outputs = model(features)
    train_loss = loss_fn(outputs, features)
    train_loss.backward()
    optimizer.step()
    return train_loss


def train(
    model: torch.nn.Module,
    data_loader: torch.utils.data.DataLoader,
    epochs: int,
    loss: object,
    optimizer: object,
) -> list:
    train_loss = []
    for epoch in range(epochs):
        epoch_loss = []
        for batch_features, batch_labels in data_loader:
            step_loss = train_loss(model, optimizer, batch_features, loss)
            epoch_loss.append(step_loss.item())
        epoch_loss = torch.mean(epoch_loss)
        train_loss.append(epoch_loss)
    return train_loss
