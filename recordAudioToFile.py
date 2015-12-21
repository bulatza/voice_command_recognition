"""PyAudio record audio and save to a WAVE file."""

import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
#RECORD_SECONDS = 2
#OUTPUT_FILENAME = "output.wav"

def recAudio(outFileName, recTime):

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
	
	frames = []
	
	for i in range(0, int(RATE / CHUNK * recTime)):
		data = stream.read(CHUNK)
		frames.append(data)
		
	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(outFileName, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()
