#!/usr/bin/env python3

from os import path, listdir, getcwd
import wave
import sys
from datetime import datetime
import json
from os import path, listdir, getcwd
from vosk import Model, KaldiRecognizer, SetLogLevel

folder_path = "/"
folder_name = "audios/"
final_path = getcwd() + folder_path + folder_name
audio_files = listdir(final_path)
# You can set log level to -1 to disable debug messages
SetLogLevel(0)
# model = Model(model_name="vosk-model-en-us-0.42-gigaspeech")
model = Model(model_name="vosk-model-en-us-0.22")
for audio_file in audio_files:
    audio_path = getcwd() + folder_path + folder_name
    AUDIO_FILE = audio_path + audio_file
    wf = wave.open(AUDIO_FILE)
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        sys.exit(1)

    # model = Model(lang="en-us")

    # You can also init model by name or with a folder path
    # model = Model(model_name="vosk-model-en-us-0.21")
    # model = Model("models/en")

    start = datetime.now()
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    rec.SetPartialWords(True)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            rec.Result()
            # print(rec.Result())
        else:
            rec.PartialResult()
            # print(rec.PartialResult())
    # print(audio_file)
    end = datetime.now()
    total_time = end - start
    print(f'Total time taken for audio file {audio_file} {total_time} ')
    # print(audio_file)
    res = json.loads(rec.FinalResult())
    print(res['text'])
    print()
    print()