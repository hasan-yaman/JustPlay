import re

from Song import Song


class ParseSongs:

    def __init__(self, text):
        parsed_songs = re.split(r"\n\n+", text)
        # Remove empty strings from list
        parsed_songs = list(filter(None, parsed_songs))
        # print("Found {} songs in given text".format(len(songs)))
        self.songs = []
        for song_text in parsed_songs:
            self.songs.append(Song(song_text))
        if len(self.songs) == 0:
            # Red color
            print("\033[91m {}\033[00m".format("No valid songs found in the given text."))

    def __getitem__(self, item):
        return self.songs[item]

    def __len__(self):
        return len(self.songs)



