# -*- coding: utf-8 -*-
"""
@Time    : 2019/5/28 1:17
@File    : models.py
@Software: PyCharm
Introduction: Models for diagnosing the heart disease by the ECG.
"""
#%% Import Packages
import numpy as np
import torch
import torch.nn as nn
from transformer.transformer_block import TRANSFORMER
#%% Functions
class CNN_Transformer(nn.Module):
    def __init__(self):
        super(CNN_Transformer, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(
                in_channels=12,
                out_channels=32,
                kernel_size=(30, 1),
                stride=1,
                padding=0,
            ),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=(3, 1))
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, (10, 1), 1, 0),
            nn.ReLU(),
            nn.MaxPool2d((3, 1))
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 64, (10, 1), 1, 0),
            nn.ReLU(),
            nn.MaxPool2d((3, 1))
        )
        self.conv4 = nn.Sequential(
            nn.Conv2d(64, 64, (5, 1), 1, 0),
            nn.ReLU(),
            nn.MaxPool2d((3, 1))
        )
        self.conv5 = nn.Sequential(
            nn.Conv2d(64, 128, (5, 1), 1, 0),
            nn.ReLU(),
            nn.MaxPool2d((3, 1))
        )
        self.conv6 = nn.Sequential(
            nn.Conv2d(128, 128, (3, 1), 1, 0),
            nn.ReLU(),
            nn.MaxPool2d((3, 1))
        )
        self.conv7 = nn.Sequential(
            nn.Conv2d(128, 128, (2, 1), 1, 0),  # 直接简写了，参数的顺序同上
            nn.ReLU(),
            nn.MaxPool2d((1, 1))
        )
        self.network1 = nn.Sequential(
            nn.Linear(256, 200),  # 卷积层后加一个普通的神经网络
            # nn.BatchNorm1d(256),
            nn.Dropout(0.7),
            nn.ReLU(),
            nn.Linear(200, 128),  # 卷积层后加一个普通的神经网络
            # nn.BatchNorm1d(100),
            nn.Dropout(0.5),
            nn.ReLU(),
        )
        self.transformer = TRANSFORMER()
        self.networks2 = nn.Sequential(
            nn.Linear(128, 100),
            nn.Dropout(0.7),
            nn.Linear(100, 9),
        )
        self.dropout = nn.Dropout(0.5)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.conv5(x)
        x = self.conv6(x)
        # x = self.conv7(x)
        x = x.reshape(x.shape[0], -1)  # win_num * feature
        x = self.network1(x)
        x = x.unsqueeze(0)
        x = self.dropout(x)
        x = self.transformer(self.relu(x))
        x = x[:, -1, :]
        embedding = x.reshape(1, -1)
        x = self.networks2(embedding)
        return x, embedding

def LinkConstraints(embedding, link, weight_decay=0.1):
    # Link Constraints
    batch_size = len(embedding)
    Loss = []
    for i in range(batch_size-1):
        for j in range(i+1, batch_size):
            e = 1 if link[i] == link[j] else -1
            Loss.append((embedding[i] - (e * embedding[j])).norm(2))
    Loss = torch.stack(Loss).sum()
    Loss = Loss * 0.5 * weight_decay
    return Loss

#%% Main Function
if __name__ == '__main__':
    e = []
    for i in range(3):
        x = np.random.randn(3, 12, 3000, 1)
        x = torch.Tensor(x)
        cnn_transformer = CNN_Transformer()
        y, e1 = cnn_transformer(x)
        e.append(e1)
    print(e1.shape)
    link = [0,1,1]
    b = LinkConstraints(e, link)

