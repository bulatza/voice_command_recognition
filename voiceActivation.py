import sys, os
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *


modeldir = "../pocketsphinx-python/pocketsphinx/model"
datadir = "../pocketsphinx-python/pocketsphinx/test/data"

# Create a decoder with certain model
config = Decoder.default_config()
config.set_string('-hmm', os.path.join(modeldir, 'en-us/en-us'))
config.set_string('-dict', os.path.join(modeldir, 'en-us/cmudict-en-us.dict'))
config.set_string('-keyphrase', 'raspberry')
config.set_float('-kws_threshold', 1e-40)


# read stream with pyaudio
#import pyaudio
#p = pyaudio.PyAudio()
#stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
#stream.start_stream()

# read stream with alsaaudio
import alsaaudio

CHUNK = 1024
FORMAT = alsaaudio.PCM_FORMAT_S16_LE
CHANNELS = 1
RATE = 16000

stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL)
stream.setchannels(CHANNELS)
stream.setrate(RATE)
stream.setformat(FORMAT)
stream.setperiodsize(CHUNK)


# Process audio chunk by chunk. 
decoder = Decoder(config)
decoder.start_utt()
while True:
    #buf = stream.read(1024)
    l,data = stream.read()
    if buf:
         decoder.process_raw(buf, False, False)
    else:
         break
    if decoder.hyp() != None:
        #print ([(seg.word, seg.prob, seg.start_frame, seg.end_frame) for seg in decoder.seg()])
        print ("Detected keyword, restarting search")
        decoder.end_utt()
        decoder.start_utt()
