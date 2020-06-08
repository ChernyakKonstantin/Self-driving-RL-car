import torch.nn as nn
class myDQN(nn.Module):
    def __init__(self, n_inputs, hidden_size, n_outputs):
        super(myDQN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(n_inputs, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, n_outputs),
        )

    def forward(self, x):
        return self.net(x) #Сеть возвращает Q(s,a) для данного state и всех возможных action
