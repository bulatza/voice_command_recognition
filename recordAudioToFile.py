"""PyAudio record audio and save to a WAVE file."""

import pyaudio
import wave
import alsaaudio

CHANNELS = 1
CHUNK = 1024
RATE = 16000

FORMAT_pyaudio = pyaudio.paInt16
#RECORD_SECONDS = 2
#OUTPUT_FILENAME = "output.wav"

FORMAT_alsaaudio = alsaaudio.PCM_FORMAT_S16_LE
FORMAT_PCM_FORMAT_S16_LE_size  = 2

def recPyAudio(outFileName, recTime):

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT_pyaudio,
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
	wf.setsampwidth(p.get_sample_size(FORMAT_pyaudio))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

def recAlsaAudio(outFileName, recTime):
	stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL)
	stream.setchannels(CHANNELS)
	stream.setrate(RATE)
	stream.setformat(FORMAT_alsaaudio)
	stream.setperiodsize(CHUNK)

	frames = []

	for i in range(0, int(RATE / CHUNK * recTime)):
		l,data = stream.read()
		frames.append(data)

	wf = wave.open(outFileName, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(FORMAT_PCM_FORMAT_S16_LE_size)
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()