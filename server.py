import os

import numpy as np
import torch
from flask import Flask, request, jsonify, render_template
from torch.nn import functional as F

from model import CharRNN
from settings import *
from utils import load_dict

app = Flask(__name__)

# Create and load model
model = CharRNN(n_char)
model.load_state_dict(torch.load(default_model_path, map_location='cpu'))
model.eval()

# Load necessary dictionaries
int2char = load_dict(int2char_path)
char2int = load_dict(char2int_path)

counter = 0

print("Ready!")


@app.route("/")
def generate_song():
    return render_template("index.html")


@app.route("/api/predict", methods=["GET"])
def predict():
    title = request.args.get("title", type=str)
    composer = request.args.get("composer", type=str)
    meter = request.args.get("meter", type=str)
    key = request.args.get("key", type=str)
    length = request.args.get("length", type=str)
    prime = request.args.get("prime", default='X', type=str)
    size = request.args.get("size", default=1000, type=int)

    chars = [c for c in prime]
    # Initialize hidden state
    hidden = model.init_hidden(1)
    for c in chars:
        generated_c, hidden = forward_single_char(c, hidden)

    for _ in range(size):
        generated_c, hidden = forward_single_char(chars[-1], hidden)
        chars.append(generated_c)

    generated_song = "".join(chars)

    global counter
    abc_filename = "static/tmp" + str(counter % 20) + ".abc"
    midi_filename = "static/tmp" + str(counter % 20) + ".mid"
    wav_filename = "static/tmp" + str(counter % 20) + ".wav"
    counter += 1

    # Save abc format
    with open(abc_filename, "w") as f:
        f.write(generated_song)

    # TODO We don't know whether they are worked correctly or not
    # Convert abc file to midi
    os.system("pwd")

    cmd = "abc2midi " + abc_filename + " -o " + midi_filename
    os.system(cmd)

    # Convert midi to wav file
    cmd = "timidity " + midi_filename + " -Ow -o" + wav_filename
    os.system(cmd)

    # Delete abc and midi files
    os.remove(abc_filename)
    os.remove(midi_filename)

    # Return path of wav file
    return jsonify(wav_filename)
    # TODO delete unused files


def forward_single_char(char, hidden):
    # print("char",char)
    inputs = np.array([[char2int[char]]])
    inputs = torch.from_numpy(inputs)
    inputs.to(device)

    # detach hidden state from history
    hidden = tuple([h.data for h in hidden])
    # get the output of the model
    out, hidden = model(inputs, hidden)

    # get the character probabilities
    prob = F.softmax(out, dim=1).data

    #  get top 5 probabilities
    p, top_ch = prob.topk(5)

    p = p.numpy().squeeze()
    top_ch = top_ch.numpy().squeeze()
    # Select next char with some randomness
    char = np.random.choice(top_ch, p=p / p.sum())

    return int2char[char], hidden


if __name__ == '__main__':
    # extra_files = ["static/"]
    app.run(host="0.0.0.0", debug=True, port=8080)
