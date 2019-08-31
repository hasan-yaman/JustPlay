import os

import numpy as np
import torch
from flask import Flask, request, jsonify, render_template
from torch.nn import functional as F

from model import CharRNN
from settings import *
from utils import load_dict, create_tune_header

app = Flask(__name__)
print("Environment:", app.config["ENV"])
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
    global counter
    # Let's restrict reference number since I don't output of model with large numbers
    reference_number = str(counter % 300)
    meter = request.args.get("meter", type=str)
    key = request.args.get("key", type=str)
    tempo = request.args.get("tempo", type=str)
    rhythm = request.args.get("rhythm", type=str)
    note_length = request.args.get("note_length", type=str)

    prime = create_tune_header(fields_keys=["X", "M", "K", "Q", "R", "L"],
                               field_values=[reference_number, meter, key, tempo, rhythm, note_length])
    size = request.args.get("size", default=1000, type=int)
    print("Prime", prime)
    chars = [c for c in prime]
    print("Initialize hidden state")
    # Initialize hidden state
    hidden = model.init_hidden(1)
    print("Generate songs")
    for c in chars:
        generated_c, hidden = forward_single_char(c, hidden)

    for _ in range(size):
        generated_c, hidden = forward_single_char(chars[-1], hidden)
        chars.append(generated_c)

    generated_song = "".join(chars)

    abc_filename = "static/tmp" + str(counter % 20) + ".abc"
    midi_filename = "static/tmp" + str(counter % 20) + ".mid"
    wav_filename = "static/tmp" + str(counter % 20) + ".wav"
    counter += 1

    print("Convert to abc file")
    # Save abc format
    with open(abc_filename, "w") as f:
        f.write(generated_song)

    print("Convert to mid file")
    # TODO We don't know whether they are worked correctly or not
    # Convert abc file to midi
    cmd = "abc2midi " + abc_filename + " -o " + midi_filename
    os.system(cmd)

    print("Convert to wav file")
    # Convert midi to wav file
    if app.config["ENV"] == "production":
        cmd = "timidity --config-file .apt/etc/timidity/timidity.cfg " + midi_filename + " -Ow -o" + wav_filename
    else:
        cmd = "timidity " + midi_filename + " -Ow -o" + wav_filename
    os.system(cmd)

    print("Before deletes", os.listdir("static"))

    # Delete abc and midi files
    os.remove(abc_filename)
    os.remove(midi_filename)

    print("After deletes", os.listdir("static"))

    # Return path of wav file
    return jsonify(wav_filename)


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
    if app.config["ENV"] == "development":
        app.run(host="0.0.0.0", debug=True, port=8080)
