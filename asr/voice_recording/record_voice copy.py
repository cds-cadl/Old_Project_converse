# import pyaudio
# import wave
 
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 44100
# CHUNK = 1024
# RECORD_SECONDS = 5
# WAVE_OUTPUT_FILENAME = "file.wav"
 
# audio = pyaudio.PyAudio()
 
# # start Recording
# stream = audio.open(format=FORMAT, channels=CHANNELS,
#                 rate=RATE, input=True,
#                 frames_per_buffer=CHUNK)
# print ("recording...")
# frames = []
 
# for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#     data = stream.read(CHUNK)
#     frames.append(data)
# print ("finished recording")
 
 
# # stop Recording
# stream.stop_stream()
# stream.close()
# audio.terminate()
 
# waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# waveFile.setnchannels(CHANNELS)
# waveFile.setsampwidth(audio.get_sample_size(FORMAT))
# waveFile.setframerate(RATE)
# waveFile.writeframes(b''.join(frames))
# waveFile.close()

# from sys import byteorder
# from array import array
# from struct import pack

# import pyaudio
# import wave

# THRESHOLD = 500
# CHUNK_SIZE = 1024
# FORMAT = pyaudio.paInt16
# RATE = 44100

# def is_silent(snd_data):
#     "Returns 'True' if below the 'silent' threshold"
#     print('In Silent..', max(snd_data) < THRESHOLD)
#     return max(snd_data) < THRESHOLD

# def normalize(snd_data):
#     "Average the volume out"
#     MAXIMUM = 16384
#     times = float(MAXIMUM)/max(abs(i) for i in snd_data)

#     r = array('h')
#     for i in snd_data:
#         r.append(int(i*times))
#     return r

# def trim(snd_data):
#     "Trim the blank spots at the start and end"
#     def _trim(snd_data):
#         snd_started = False
#         r = array('h')

#         for i in snd_data:
#             if not snd_started and abs(i)>THRESHOLD:
#                 snd_started = True
#                 r.append(i)

#             elif snd_started:
#                 r.append(i)
#         return r

#     # Trim to the left
#     snd_data = _trim(snd_data)

#     # Trim to the right
#     snd_data.reverse()
#     snd_data = _trim(snd_data)
#     snd_data.reverse()
#     return snd_data

# def add_silence(snd_data, seconds):
#     "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
#     silence = [0] * int(seconds * RATE)
#     r = array('h', silence)
#     r.extend(snd_data)
#     r.extend(silence)
#     return r

# def record():
#     """
#     Record a word or words from the microphone and 
#     return the data as an array of signed shorts.

#     Normalizes the audio, trims silence from the 
#     start and end, and pads with 0.5 seconds of 
#     blank sound to make sure VLC et al can play 
#     it without getting chopped off.
#     """
#     p = pyaudio.PyAudio()
#     stream = p.open(format=FORMAT, channels=1, rate=RATE,
#         input=True, output=True,
#         frames_per_buffer=CHUNK_SIZE)

#     num_silent = 0
#     snd_started = False

#     r = array('h')
#     try:
#         while 1:
#             # little endian, signed short
#             snd_data = array('h', stream.read(CHUNK_SIZE))
#             if byteorder == 'big':
#                 snd_data.byteswap()
#             r.extend(snd_data)

#             silent = is_silent(snd_data)

#             if silent and snd_started:
#                 num_silent += 1
#             elif not silent and not snd_started:
#                 snd_started = True

#             if snd_started and num_silent > 1:
#                 break
#     except:
#         print('Breaking...')
#     sample_width = p.get_sample_size(FORMAT)
#     stream.stop_stream()
#     stream.close()
#     p.terminate()

#     # r = normalize(r)
#     r = trim(r)
#     r = add_silence(r, 0.5)
#     return sample_width, r

# def record_to_file(path):
#     "Records from the microphone and outputs the resulting data to 'path'"
#     sample_width, data = record()
#     data = pack('<' + ('h'*len(data)), *data)

#     wf = wave.open(path, 'wb')
#     wf.setnchannels(1)
#     wf.setsampwidth(sample_width)
#     wf.setframerate(RATE)
#     wf.writeframes(data)
#     wf.close()

# if __name__ == '__main__':
#     print("please speak a word into the microphone")
#     record_to_file('demo.wav')
#     print("done - result written to demo.wav")
'''
Instead of adding silence at start and end of recording (values=0) I add the original audio . This makes audio sound more natural as volume is >0. See trim()
I also fixed issue with the previous code - accumulated silence counter needs to be cleared once recording is resumed.
'''
from array import array
from struct import pack
from sys import byteorder
import copy
import pyaudio
import wave

THRESHOLD = 500  # audio levels not normalised.
CHUNK_SIZE = 1024
SILENT_CHUNKS = 1 * 44100 / 1024  # about 3sec
FORMAT = pyaudio.paInt16
FRAME_MAX_VALUE = 2 ** 15 - 1
NORMALIZE_MINUS_ONE_dB = 10 ** (-1.0 / 20)
RATE = 44100
CHANNELS = 1
TRIM_APPEND = RATE / 4

def is_silent(data_chunk):
    """Returns 'True' if below the 'silent' threshold"""
    return max(data_chunk) < THRESHOLD

def normalize(data_all):
    """Amplify the volume out to max -1dB"""
    # MAXIMUM = 16384
    normalize_factor = (float(NORMALIZE_MINUS_ONE_dB * FRAME_MAX_VALUE)
                        / max(abs(i) for i in data_all))

    r = array('h')
    for i in data_all:
        r.append(int(i * normalize_factor))
    return r

def trim(data_all):
    _from = 0
    _to = len(data_all) - 1
    for i, b in enumerate(data_all):
        if abs(b) > THRESHOLD:
            _from = max(0, i - TRIM_APPEND)
            break

    for i, b in enumerate(reversed(data_all)):
        if abs(b) > THRESHOLD:
            _to = min(len(data_all) - 1, len(data_all) - 1 - i + TRIM_APPEND)
            break

    return copy.deepcopy(data_all[_from:(_to + 1)])

def record():
    """Record a word or words from the microphone and 
    return the data as an array of signed shorts."""

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK_SIZE)

    silent_chunks = 0
    audio_started = False
    data_all = array('h')
    try:
        while True:
            # little endian, signed short
            data_chunk = array('h', stream.read(CHUNK_SIZE))
            if byteorder == 'big':
                data_chunk.byteswap()
            data_all.extend(data_chunk)

            silent = is_silent(data_chunk)

            if audio_started:
                if silent:
                    silent_chunks += 1
                    if silent_chunks > SILENT_CHUNKS:
                        break
                else: 
                    silent_chunks = 0
            elif not silent:
                audio_started = True              
    except:
        print('breaking')
    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    data_all = trim(data_all)  # we trim before normalize as threshhold applies to un-normalized wave (as well as is_silent() function)
    data_all = normalize(data_all)
    return sample_width, data_all

def record_to_file(path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    data = pack('<' + ('h' * len(data)), *data)

    wave_file = wave.open(path, 'wb')
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(sample_width)
    wave_file.setframerate(RATE)
    wave_file.writeframes(data)
    wave_file.close()

if __name__ == '__main__':
    print("Wait in silence to begin recording; wait in silence to terminate")
    record_to_file('demo.wav')
    print("done - result written to demo.wav")

# """PyAudio Example: Play a wave file (callback version)."""

# import wave
# import time
# import sys

# import pyaudio


# if len(sys.argv) < 2:
#     print(f'Plays a wave file. Usage: {sys.argv[0]} filename.wav')
#     sys.exit(-1)

# with wave.open(sys.argv[1], 'rb') as wf:
#     # Define callback for playback (1)
#     def callback(in_data, frame_count, time_info, status):
#         data = wf.readframes(frame_count)
#         # If len(data) is less than requested frame_count, PyAudio automatically
#         # assumes the stream is finished, and the stream stops.
#         return (data, pyaudio.paContinue)

#     # Instantiate PyAudio and initialize PortAudio system resources (2)
#     p = pyaudio.PyAudio()

#     # Open stream using callback (3)
#     stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                     channels=wf.getnchannels(),
#                     rate=wf.getframerate(),
#                     output=True,
#                     stream_callback=callback)

#     # Wait for stream to finish (4)
#     while stream.is_active():
#         time.sleep(0.1)

#     # Close the stream (5)
#     stream.close()

#     # Release PortAudio system resources (6)
#     p.terminate()

# import threading
# from array import array
# from queue import Queue, Full
# from struct import pack

# import pyaudio


# CHUNK_SIZE = 1024
# MIN_VOLUME = 500
# # if the recording thread can't consume fast enough, the listener will start discarding
# BUF_MAX_SIZE = CHUNK_SIZE * 10


# def main():
#     stopped = threading.Event()
#     q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))

#     listen_t = threading.Thread(target=listen, args=(stopped, q))
#     listen_t.start()
#     record_t = threading.Thread(target=record, args=(stopped, q))
#     record_t.start()

#     try:
#         while True:
#             listen_t.join(0.1)
#             record_t.join(0.1)
#     except KeyboardInterrupt:
#         stopped.set()

#     listen_t.join()
#     record_t.join()

# def record_to_file(path):
#     "Records from the microphone and outputs the resulting data to 'path'"
#     sample_width, data = record()
#     data = pack('<' + ('h' * len(data)), *data)

#     wave_file = wave.open(path, 'wb')
#     wave_file.setnchannels(CHANNELS)
#     wave_file.setsampwidth(sample_width)
#     wave_file.setframerate(RATE)
#     wave_file.writeframes(data)
#     wave_file.close()


# def record(stopped, q):
#     while True:
#         if stopped.wait(timeout=0):
#             break
#         chunk = q.get()
#         vol = max(chunk)
#         if vol >= MIN_VOLUME:
#             # TODO: write to file
#             print("O")
#         else:
#             print("-")


# def listen(stopped, q):
#     stream = pyaudio.PyAudio().open(
#         format=pyaudio.paInt16,
#         channels=1,
#         rate=44100,
#         input=True,
#         frames_per_buffer=1024,
#     )

#     while True:
#         if stopped.wait(timeout=0):
#             break
#         try:
#             q.put(array('h', stream.read(CHUNK_SIZE)))
#         except Full:
#             pass  # discard


# if __name__ == '__main__':
#     main()