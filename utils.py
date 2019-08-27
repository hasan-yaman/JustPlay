import os
import pickle


def load_dict(path):
    f = open(path, "rb")
    d = pickle.load(f)
    f.close()
    return d


def delete_old_sound_files(wav_files_list):
    # Find modification date of .wav files and sort them using the modification date
    wav_files = dict()

    for f in wav_files_list:
        wav_files[f] = os.path.getmtime("static/" + f)

    wav_files = sorted(wav_files.items(), key=lambda x: x[1])

    # Delete the oldest 5 file
    for f in wav_files[:5]:
        os.remove("static/" + f[0])
