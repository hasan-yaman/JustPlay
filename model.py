import torch
from torch import nn


class CharRNN(nn.Module):
    def __init__(self, n_chars):
        super().__init__()
        lstm_input_size = 256  #  also output size of embedding layer
        self.hidden_size = 1024
        self.num_layers = 2
        dropout = 0.5

        self.embed = nn.Embedding(n_chars, lstm_input_size)
        self.lstm = nn.LSTM(input_size=lstm_input_size, hidden_size=self.hidden_size, num_layers=self.num_layers,
                            dropout=dropout, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(self.hidden_size, n_chars)

    def forward(self, x, hidden):
        x = self.embed(x)
        x, hidden = self.lstm(x, hidden)
        x = self.dropout(x)
        # Stack up LSTM outputs using view
        # we may need to use contiguous to reshape the output
        x = x.contiguous().view(-1, self.hidden_size)
        x = self.linear(x)
        return x, hidden

    def init_hidden(self, batch_size):
        ''' Initializes hidden state '''
        # Create two new tensors with sizes n_layers x batch_size x n_hidden,
        # initialized to zero, for hidden state and cell state of LSTM
        weight = next(self.parameters()).data
        h = weight.new(self.num_layers, batch_size, self.hidden_size).zero_()
        c = weight.new(self.num_layers, batch_size, self.hidden_size).zero_()
        if torch.cuda.is_available():
            h = h.cuda()
            c = c.cuda()
        hidden = (h, c)
        return hidden
