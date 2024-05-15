from openai import OpenAI
import speech_recognition as sr
from datetime import datetime
from os import path, listdir, getcwd

r = sr.Recognizer()

times_by_ggl = {}
times_by_whisper = {}

# Get all audio files
audio_files = listdir(getcwd() + "/audio_files/")

def time_taken_google_speech(audio):
    start = datetime.now()
    # recognize speech using Google Speech Recognition
    try:
        r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    end = datetime.now()
    total_time = end - start
    return total_time

def time_taken_openAI_whisper(audio):
    start = datetime.now()
    try:
        r.recognize_whisper(audio)
    except sr.UnknownValueError:
        print("Did not understand")
    except sr.RequestError as e:
        print(e)
    end = datetime.now()
    total_time = end - start
    return total_time


for audio_file in audio_files:
    print(audio_file)
    AUDIO_FILE = getcwd() + "/audio_files/" + audio_file

    # use the audio file as the audio source
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file
    print(f"Processing Audio file - {audio_file}")
    print()
    print("Time taken by Google Speech Recognition")
    tt_ggl = time_taken_google_speech(audio)
    print(tt_ggl)
    times_by_ggl[audio_file] = tt_ggl

    print("Time taken by OpenAI Whisper")
    tt_whisper = time_taken_google_speech(audio)
    print(tt_whisper)
    times_by_whisper[audio_file] = tt_whisper
    print()

total_times_ggl = sum(times_by_ggl.values())
total_times_whisper = sum(times_by_whisper.values())

print(times_by_ggl)
print(times_by_whisper)

print(f'Total time taken by Google Speech Recognition to process {len(audio_files)} audio files is {total_times_ggl}')
print(f'Total time taken by OpenAI Whisper to process {len(audio_files)} audio files is {total_times_whisper}')