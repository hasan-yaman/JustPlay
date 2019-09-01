# Just Play

[Live Demo](https://hasanyaman.tech)

A CharRNN to create some music.The inspiration comes from 
[MIT Lectures.](https://github.com/aamini/introtodeeplearning_labs)


## Dataset
I used subset of [Nottingham Music Database](http://abc.sourceforge.net/NMD/).To be more precise I used the following 
collections:
- Jigs
- Hornpipes
- Morris
- Playford
- Reels A-C
- Reels D-G
- Reels H-L

Each collection contains 15 to 340 different tunes. In total I used 709 different tunes. I randomly selected 20% of 
tunes for the validation set.

## Network Structure
The neural network have 4 layers.
1. Embedding Layer
    - Input Size:92
    - Output Size: 256
2. Two LSTM Layers
    - Input Size: 256
    - Output Size: 1024
3. Fully Connected Linear Layer
    - Input Size: 1024
    - Output Size: 92
    
I used Google Colab to train the neural network.

## Deployment
I used Flask framework to create the web application. For deployment platform, my choice was Heroku.
To run locally, first install necessary packages:
```
apt-get install abcmidi timidity
pip install flask
```
Set environment variables:
```
export FLASK_APP=server.py
export FLASK_ENV=development
```
Then run:
```
flask run
```
*I only tested on macOS High Sierra.*

## TODO
- [ ] Add download option for created musics.
- [ ] Try different networks.
- [ ] Add different networks to web application.
- [ ] Use different data sources.(different music genres?)
- [ ] Add tests :smile:

