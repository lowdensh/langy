import torch
import torch.nn as nn


class LangyBlock(nn.Module):
    """
    A block for a LangyNet model consisting of:
    - linear hidden layer
    - rectified linear activation function
    - dropout layer.

    Initialisation Parameters
    -------------------------
    id : int
        Block identification number.
    input_nodes : int
        Input size for the hidden layer.
    output_nodes : int
        Output size for the hidden layer i.e. number of hidden nodes.
    p_dropout : float, default=0
        Probability of a hidden layer node to be zeroed.

    Forward Parameters
    ------------------
    x : Tensor
        Size([batch_size, input_nodes])

    Returns
    -------
    x : Tensor
        Size([batch_size, output_nodes])

    """

    def __init__(self, id, input_nodes, output_nodes, p_dropout=0):
        super(LangyBlock, self).__init__()
        self.id = id
        self.input_nodes = input_nodes
        self.output_nodes = output_nodes
        self.p_dropout = p_dropout

        self.add_module(
            f'hid{self.id}',
            nn.Linear(self.input_nodes, self.output_nodes))
        self.add_module(
            f'act{self.id}',
            nn.ReLU())
        self.add_module(
            f'drop{self.id}',
            nn.Dropout(self.p_dropout))

    def forward(self, x):
        x = self._modules[f'hid{self.id}'](x)
        x = self._modules[f'act{self.id}'](x)
        x = self._modules[f'drop{self.id}'](x)
        return x


class LangyNet(nn.Module):
    """
    A Multilayer Perceptron with a configurable number of hidden layers.

    Takes a Tensor of learning traces and produces a prediction for the
    probability that the represented foreign word can be correctly translated.

    Initialisation Parameters
    -------------------------
    hidden_layers : int
        Number of hidden layers i.e. LangyBlocks to use.
    hidden_nodes : int
        Number of nodes to use in hidden layers.
    p_dropout : float, default=0
        Probability of a hidden layer node to be zeroed.

    Forward Parameters
    ------------------
    x : Tensor
        Tensor of learning traces, Size([batch_size, 10])

    Returns
    -------
    p_trans : Tensor
        Probability of correct translation, Size([batch_size, 1])
    """

    def __init__(self, hidden_layers, hidden_nodes, p_dropout=0):
        super(LangyNet, self).__init__()
        self.input_features = 10  # delta, seen, ..., frn_4
        self.output_features = 1  # p_trans
        self.hidden_layers = hidden_layers
        self.hidden_nodes = hidden_nodes
        self.p_dropout = p_dropout

        # Add hidden layers
        for i in range(hidden_layers):
            if i == 0:
                # First hidden layer
                self.add_module(
                    f'langy_block_{i+1}',
                    LangyBlock(i+1, self.input_features, self.hidden_nodes, self.p_dropout))
            else:
                # Additional hidden layers
                self.add_module(
                    f'langy_block_{i+1}',
                    LangyBlock(i+1, self.hidden_nodes, self.hidden_nodes, self.p_dropout))
            
        # Output layer
        self.output = nn.Linear(self.hidden_nodes, self.output_features)
        

    def forward(self, x):
        for i in range(self.hidden_layers):
            x = self._modules[f'langy_block_{i+1}'](x)
        x = self.output(x)
        return x
