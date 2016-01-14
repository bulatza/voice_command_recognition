
# -*- coding: utf-8 -*-

import logging
import click
import exceptions

import asrclient.client as client

try:
    import pyaudio
    is_pyaudio = True
except exceptions.ImportError:
    is_pyaudio = False

#default arguments
key = u'3e83871d-fa02-4b05-b9bf-58a0d498ca2b'
server = u'asr.yandex.net'
port = 80
#default is audio/x-pcm;bit=16;rate=16000.
format = u'audio/x-pcm;bit=16;rate=16000'
model = u'freeform'
lang = u'ru-RU'
chunk_size = 65536
start_with_chunk = 0
max_chunks_count = None
silent = True
reconnect_delay = 0.5
reconnect_retry_count = 5
record = False
ipv4 = False
nopunctuation = True
uuid = u'9782b53d4d6c4a8e8c97e1787da232ea'
#files = 'out.wav'

# callback variable
recognized_text = ''

def text_callback(yandex_text):
    global recognized_text
    recognized_text = yandex_text

def yandexASR(key, server, port, format, model, lang, chunk_size, start_with_chunk, max_chunks_count, silent, reconnect_delay, reconnect_retry_count, record, ipv4, nopunctuation, uuid, files):
    results = ""
    print ('**start yandexASR')
    if not silent:
        logging.basicConfig(level=logging.INFO)

    chunks = []
    if files:
        f = open(files, 'rb')
        chunks = client.read_chunks_from_files(f,
                                               chunk_size,
                                               start_with_chunk,
                                               max_chunks_count)
    else:
        if record:
            if is_pyaudio:
                chunks = client.read_chunks_from_pyaudio(chunk_size)
                print ("size of chunks" + len(chunks))
            else:
                click.echo('Please install pyaudio module for system audio recording.')
                sys.exit(-2)

    if not chunks:
        click.echo('Please, specify one or more input filename.')
    else:
        results = client.recognize(chunks,
                         callback= text_callback,#click.echo,
                         host=server,
                         port=port,
                         key=key,
                         format=format,
                         topic=model,
                         lang=lang,
                         reconnect_delay=reconnect_delay,
                         reconnect_retry_count=reconnect_retry_count,                         
                         uuid=uuid,
                         ipv4=ipv4,
                         punctuation=not nopunctuation)
    
    print ('**finished yandexASR')
    return results
    
def  yandexAsrFile(audioFile):
    results = ""
    if not silent:
        logging.basicConfig(level=logging.INFO)

    chunks = []
    f = open(audioFile, 'rb')
    chunks = client.read_chunks_from_files(f,
                                            chunk_size,
                                            start_with_chunk,
                                            max_chunks_count)
    if not chunks:
        click.echo('Please, specify one or more input filename.')
    else:
        results = client.recognize(chunks,
                         callback= click.echo,
                         host=server,
                         port=port,
                         key=key,
                         format=format,
                         topic=model,
                         lang=lang,
                         reconnect_delay=reconnect_delay,
                         reconnect_retry_count=reconnect_retry_count,                         
                         uuid=uuid,
                         ipv4=ipv4,
                         punctuation=not nopunctuation)
    f.close()
    return results

def  yandexAsrMicPyaudio():
    chunks = [] 
    if is_pyaudio:
        chunks = client.read_chunks_from_pyaudio(chunk_size)
    else:
        click.echo('Please install pyaudio module for system audio recording.')
        sys.exit(-2)

    if not chunks:
        click.echo('Please, specify one or more input filename.')
    else:
        client.recognize(chunks,
                 callback= text_callback,
                 host=server,
                 port=port,
                 key=key,
                 format=format,
                 topic=model,
                 lang=lang,
                 reconnect_delay=reconnect_delay,
                 reconnect_retry_count=reconnect_retry_count,                         
                 uuid=uuid,
                 ipv4=ipv4,
                 punctuation=not nopunctuation)

def  yandexAsrMicStream(stream, rate, chunk_size, rec_sec):
    chunks = []
    chunks = client.read_chunks_from_alsaaudio(stream, rate, chunk_size, rec_sec)

    if not chunks:
        click.echo('Please, specify one or more input filename.')
    else:
        client.recognize(chunks,
                 callback= text_callback,
                 host=server,
                 port=port,
                 key=key,
                 format=format,
                 topic=model,
                 lang=lang,
                 reconnect_delay=reconnect_delay,
                 reconnect_retry_count=reconnect_retry_count,                         
                 uuid=uuid,
                 ipv4=ipv4,
                 punctuation=not nopunctuation)
    return recognized_text
