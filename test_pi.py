import sys, os
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
import pyaudio
import time

modeldir = "/home/pi/irControl/pocketsphinx-python/pocketsphinx/model"
datadir = "/home/pi/irControl/pocketsphinx-python/pocketsphinx/test/data"

# Create a decoder with certain model
config = Decoder.default_config()
config.set_string('-hmm', os.path.join(modeldir, 'en-us/en-us'))
config.set_string('-dict', os.path.join(modeldir, 'en-us/cmudict-en-us.dict'))
config.set_string('-keyphrase', 'forward')
config.set_float('-kws_threshold', 1e-20)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

p = pyaudio.PyAudio()

#stream = p.open(format=FORMAT,
#                channels=CHANNELS,
#                rate=RATE,
#                input=True,
#                frames_per_buffer=CHUNK)

def callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                stream_callback=callback)

stream.start_stream()


stream.start_stream()

# Process audio chunk by chunk. 
decoder = Decoder(config)
decoder.start_utt()
while True:
    buf = []
    try:
        buf = stream.read(CHUNK)
        print ("buf ok")
    except IOError as ex:
        if ex[1] != pyaudio.paInputOverflowed:
            print ("buf err")
            raise

  
    if buf:
        decoder.process_raw(buf, False, False)
    else:
        break
    if decoder.hyp() != None:
        #print ([(seg.word, seg.prob, seg.start_frame, seg.end_frame) for seg in decoder.seg()])
        print ("Detected keyword, restarting search")
        decoder.end_utt()
        decoder.start_utt()
