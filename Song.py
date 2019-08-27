import os

from IPython.display import Audio


class Song:
    def __init__(self, text):
        self.text = text
        self.abc_filename = "tmp.abc"
        self.wav_filename = "tmp.wav"

    def play(self):
        self._save_song_to_abc()
        ret = self._abc2wav()
        if ret == 0:
            return Audio(self.wav_filename)
        else:
            print("\033[91m {}\033[00m".format("The song cannot be played."))

    def _save_song_to_abc(self):
        with open(self.abc_filename, "w") as f:
            f.write(self.text)

    def _abc2wav(self):
        # TODO Instead of bash script, maybe I can use os.system().Is it OS independent?
        path_to_tool = './abc2wav'  # Worked in MacOS, I should test other operating systems.
        cmd = "{} {}".format(path_to_tool, self.abc_filename)
        return os.system(cmd)

    def __str__(self) -> str:
        return self.text
