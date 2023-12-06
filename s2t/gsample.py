# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.

NOTE: This module requires the dependencies `pyaudio` and `termcolor`.
To install using pip:

    pip install pyaudio
    pip install termcolor

Example usage:
    python transcribe_streaming_infinite.py
"""

# [START speech_transcribe_infinite_streaming]

import queue, io
import base64
import re
import sys, wave
import time

from pydub import AudioSegment
from pydub.playback import play
import configparser
config = configparser.ConfigParser()
config.read('./.config')
print (config.get('OPENAI','OPENAI_API_KEY'))

# from google.cloud import speech
import pyaudio
import openai, threading
openai.api_key = config.get('OPENAI','OPENAI_API_KEY')

# Audio recording parameters
STREAMING_LIMIT = 0.1 * 60 # 4 minutes
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"


# def get_current_time() -> int:
#     """Return Current Time in MS.

#     Returns:
#         int: Current Time in MS.
#     """

#     return int(round(time.time() * 1000))


# class ResumableMicrophoneStream:
#     """Opens a recording stream as a generator yielding the audio chunks."""

#     def __init__(
#         self: object,
#         rate: int,
#         chunk_size: int,
#     ) -> None:
#         """Creates a resumable microphone stream.

#         Args:
#         self: The class instance.
#         rate: The audio file's sampling rate.
#         chunk_size: The audio file's chunk size.

#         returns: None
#         """
#         self._rate = rate
#         self.chunk_size = chunk_size
#         self._num_channels = 1
#         self._buff = queue.Queue()
#         self.closed = True
#         self.start_time = get_current_time()
#         self.restart_counter = 0
#         self.audio_input = []
#         self.last_audio_input = []
#         self.result_end_time = 0
#         self.is_final_end_time = 0
#         self.final_request_end_time = 0
#         self.bridging_offset = 0
#         self.last_transcript_was_final = False
#         self.new_stream = True
#         self._audio_interface = pyaudio.PyAudio()
#         self._audio_stream = self._audio_interface.open(
#             format=pyaudio.paInt16,
#             channels=self._num_channels,
#             rate=self._rate,
#             input=True,
#             frames_per_buffer=self.chunk_size,
#             # Run the audio stream asynchronously to fill the buffer object.
#             # This is necessary so that the input device's buffer doesn't
#             # overflow while the calling thread makes network requests, etc.
#             stream_callback=self._fill_buffer,
#         )

#     def __enter__(self: object) -> object:
#         """Opens the stream.

#         Args:
#         self: The class instance.

#         returns: None
#         """
#         self.closed = False
#         return self

#     def __exit__(
#         self: object,
#         type: object,
#         value: object,
#         traceback: object,
#     ) -> object:
#         """Closes the stream and releases resources.

#         Args:
#         self: The class instance.
#         type: The exception type.
#         value: The exception value.
#         traceback: The exception traceback.

#         returns: None
#         """
#         self._audio_stream.stop_stream()
#         self._audio_stream.close()
#         self.closed = True
#         # Signal the generator to terminate so that the client's
#         # streaming_recognize method will not block the process termination.
#         self._buff.put(None)
#         self._audio_interface.terminate()

#     def _fill_buffer(
#         self: object,
#         in_data: object,
#         *args: object,
#         **kwargs: object,
#     ) -> object:
#         """Continuously collect data from the audio stream, into the buffer.

#         Args:
#         self: The class instance.
#         in_data: The audio data as a bytes object.
#         args: Additional arguments.
#         kwargs: Additional arguments.

#         returns: None
#         """
#         self._buff.put(in_data)
#         return None, pyaudio.paContinue

#     def generator(self: object) -> object:
#         """Stream Audio from microphone to API and to local buffer

#         Args:
#             self: The class instance.

#         returns:
#             The data from the audio stream.
#         """

#         # print("called generator")
#         while not self.closed:
#             print("called generator")
#             data = []

#             if self.new_stream and self.last_audio_input:
#                 chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

#                 if chunk_time != 0:
#                     if self.bridging_offset < 0:
#                         self.bridging_offset = 0

#                     if self.bridging_offset > self.final_request_end_time:
#                         self.bridging_offset = self.final_request_end_time

#                     chunks_from_ms = round(
#                         (self.final_request_end_time - self.bridging_offset)
#                         / chunk_time
#                     )

#                     self.bridging_offset = round(
#                         (len(self.last_audio_input) - chunks_from_ms) * chunk_time
#                     )

#                     for i in range(chunks_from_ms, len(self.last_audio_input)):
#                         data.append(self.last_audio_input[i])

#                 self.new_stream = False

#             # Use a blocking get() to ensure there's at least one chunk of
#             # data, and stop iteration if the chunk is None, indicating the
#             # end of the audio stream.
#             chunk = self._buff.get()
#             self.audio_input.append(chunk)

#             if chunk is None:
#                 return
#             data.append(chunk)
#             # Now consume whatever other data's still buffered.
#             while True:
#                 try:
#                     chunk = self._buff.get(block=False)

#                     if chunk is None:
#                         return
#                     data.append(chunk)
#                     self.audio_input.append(chunk)

#                 except queue.Empty:
#                     break

#             # print(b"".join(data))
#             yield b"".join(data)


# def main() -> None:
#     """start bidirectional streaming from microphone input to speech API"""

#     mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)
#     print(mic_manager.chunk_size)
#     sys.stdout.write(YELLOW)
#     sys.stdout.write('\nListening, say "Quit" or "Exit" to stop.\n\n')
#     sys.stdout.write("End (ms)       Transcript Results/Status\n")
#     sys.stdout.write("=====================================================\n")

#     with mic_manager as stream:
#         while not stream.closed:
#             sys.stdout.write(YELLOW)
#             # sys.stdout.write(
#             #     "\n" + str(STREAMING_LIMIT * stream.restart_counter) + ": NEW REQUEST\n"
#             # )

#             stream.audio_input = []
#             audio_generator = stream.generator()
#             audio = b""
#             for chunk in audio_generator:
#                 audio += chunk
#                 if len(audio) >= CHUNK_SIZE:
#                     audio_base64 = base64.b64encode(audio).decode('utf-8')
#                     audio_bytes = base64.b64decode(audio_base64)

#                     audion = AudioSegment.from_mp3(io.BytesIO(audio_bytes))

#                     # Play the audio
#                     play(audion)
#                 #     response = openai.Audio.transcribe(
#                 #     audio = audio_base64,
#                 #     model = "whisper-1",
#                 #     response_format="text",
#                 #     language="en"
#                 # )

#                 #     transcription = response['text']
#                 #     print(transcription, response)
#                     break

            
#             # audio = b"".join(chunk for chunk in audio_generator)
#             # print( [content for content in audio_generator])
#             # print(audio)

#             # fname = "sample.mp3"
#             # buffer = io.BytesIO()
#             # # you need to set the name with the extension
#             # buffer.name = fname
#             # audio.export(buffer, format="mp3")
#             # transcript = openai.Audio.transcribe(
#             #         file = buffer,
#             #         model = "whisper-1",
#             #         response_format="text",
#             #         language="en"
#             #     )
#             # print(transcript)

#             if get_current_time() - stream.start_time > STREAMING_LIMIT:
#                 stream.start_time = get_current_time()
#                 print("limit hit")
#                 # audio_generator = stream.generator()
#                 stream.closed = True


#             # Now, put the transcription responses to use.
#             if stream.result_end_time > 0:
#                 stream.final_request_end_time = stream.is_final_end_time
#             stream.result_end_time = 0
#             stream.last_audio_input = []
#             stream.last_audio_input = stream.audio_input
#             stream.audio_input = []
#             stream.restart_counter = stream.restart_counter + 1

#             # if not stream.last_transcript_was_final:
#             #     # sys.stdout.write("recording\n")
#             stream.new_stream = True



# if __name__ == "__main__":
#     main()

# # [END speech_transcribe_infinite_streaming]


# # Set your OpenAI API key here
# openai.api_key = "YOUR_OPENAI_API_KEY"

# Audio recording parameters

# Audio recording parameters
# SAMPLE_RATE = 16000
# CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms

# # Create a thread-safe queue to store audio chunks
# audio_chunk_queue = queue.Queue()

# # Create a variable to indicate when to stop recording
# stop_recording = False

# # Create an AudioSegment to store the full audio recording
# full_audio = AudioSegment.empty()

# # Define a function to start the microphone stream
# def start_microphone_stream():
#     global stop_recording
#     global full_audio

#     audio_interface = pyaudio.PyAudio()
#     audio_stream = audio_interface.open(
#         format=pyaudio.paInt16,
#         channels=1,
#         rate=SAMPLE_RATE,
#         input=True,
#         frames_per_buffer=CHUNK_SIZE,
#     )

#     start_time = time.time()

#     while not stop_recording:
#         try:
#             audio_chunk = audio_stream.read(CHUNK_SIZE)
#             audio_chunk_queue.put(audio_chunk)
#             full_audio += AudioSegment(data=audio_chunk, sample_width=2, frame_rate=SAMPLE_RATE, channels=1)

#             # Check if the recording duration exceeds 2 minutes (120 seconds)
#             if time.time() - start_time >= 100:
#                 stop_recording = True
#                 print(full_audio)
#         except Exception as e:
#             print(f"Error recording audio: {str(e)}")

#     audio_stream.stop_stream()
#     audio_stream.close()
#     audio_interface.terminate()

# # Define a function to transcribe audio using OpenAI
# def transcribe_audio():
#     global stop_recording

#     try:
#         while not stop_recording:
#             if not audio_chunk_queue.empty():
#                 audio_chunk = audio_chunk_queue.get()

#                 # Save the audio chunk as a WAV file
#                 with wave.open("recording.wav", "wb") as wav_file:
#                     wav_file.setnchannels(1)
#                     wav_file.setsampwidth(2)
#                     wav_file.setframerate(SAMPLE_RATE)
#                     wav_file.writeframes(audio_chunk)

#                 # Perform audio transcription using OpenAI
#                 response = openai.Audio.transcribe(
#                     file=open("recording.wav", "rb"),
#                     model="whisper-1",
#                     response_format="text",
#                     language="en",
#                 )
#                 # transcript = response["text"]
#                 print("Transcript:", response)
#     except KeyboardInterrupt:
#         stop_recording = True

# if __name__ == "__main__":
    # Start the microphone stream in a separate thread
    # microphone_thread = threading.Thread(target=start_microphone_stream)
    # microphone_thread.start()

    # # Transcribe the audio in the main thread
    # transcribe_audio()

    # # Wait for the microphone thread to finish
    # microphone_thread.join()


import sounddevice as sd
import numpy as np
import tempfile
import openai
import base64, subprocess

# Set your OpenAI API key here
openai.api_key = "YOUR_OPENAI_API_KEY"

# Audio recording parameters
SAMPLE_RATE = 16000
DTYPE = np.int16
MAX_RECORDING_LENGTH_SECONDS = 5  # 2 minutes

# Initialize variables to store audio data
audio_data = []

def audio_callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    if any(indata):
        audio_data.append(indata.copy())

# Start recording audio
with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, dtype=DTYPE):
    sd.sleep(MAX_RECORDING_LENGTH_SECONDS * 1000)

# Concatenate recorded audio data
audio_array = np.concatenate(audio_data, axis=0)

# Create a temporary WAV file to store the audio
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
    temp_wav.write(audio_array.tobytes())
    temp_wav.seek(0)

    # Convert the temporary WAV file to MP3
    mp3_filename = temp_wav.name.replace(".wav", ".mp3")
    # Load the WAV file using pydub
    ffmpeg_cmd = f"ffmpeg -i {temp_wav.name} -f mp3 -ab 16000 -vn {mp3_filename}"
    subprocess.run(ffmpeg_cmd, shell=True, check=True)

    # Load the MP3 file using pydub
    audio = AudioSegment.from_mp3(mp3_filename)

    # Export the audio to MP3 format
    audio.export(mp3_filename, format="mp3", bitrate="16k")

# Read the MP3 file and convert it to base64
with open(mp3_filename, "rb") as mp3_file:
    audio_base64 = base64.b64encode(mp3_file.read()).decode("utf-8")

# Transcribe the audio using OpenAI
response = openai.Audio.transcribe(
    file=audio_base64,
    model="whisper-1",
    response_format="text",
    language="en",
)

transcription = response["text"]
print("Transcription:", transcription)



