from flask import Flask, request
import json
app = Flask(__name__)

from os import path, listdir, getcwd
import wave
import sys
from datetime import datetime

from vosk import Model, KaldiRecognizer, SetLogLevel

# You can set log level to -1 to disable debug messages
SetLogLevel(0)
# model = None
# @app.route("/get_text", methods=["POST"])
@app.route("/get_text/<audio_file>")
def get_text(audio_file):
    folder_path = "/"
    folder_name = "audios/"
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
    final_result = json.loads(rec.FinalResult())
    final_result = final_result['text']+'\n'
    # print(audio_file)
    # print(rec.FinalResult())
    print()
    # print(type (rec.FinalResult()))
    print()
    print(final_result)
    # print('text')
    # print(final_result['text'])
    print()
    # return final_result, 200
    return f'Results for audio file {audio_file}:\n converted text - {final_result}\n total time - {total_time}\n', 200

@app.route("/test", methods=["GET"])
def test():
    return 'hello', 200


@app.route("/get_text_from_audio", methods=["POST"])
# @app.route("/get_text/<audio_file>")
def get_text_from_audio():
    print('get_text_from_audio')
    # js = request.data
    # print(js)
    with open('myfile.wav', mode='bx') as f:
        f.write(request.data)
    return request, 200

    # folder_path = "/audio_files/audio-stimuli/"
    # folder_name = "7/"
    # audio_path = getcwd() + folder_path + folder_name
    # AUDIO_FILE = audio_path + audio_file
    # wf = wave.open(AUDIO_FILE)
    # if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    #     print("Audio file must be WAV format mono PCM.")
    #     sys.exit(1)

    # # model = Model(lang="en-us")

    # # You can also init model by name or with a folder path
    # # model = Model(model_name="vosk-model-en-us-0.21")
    # # model = Model("models/en")

    # start = datetime.now()
    # rec = KaldiRecognizer(model, wf.getframerate())
    # rec.SetWords(True)
    # rec.SetPartialWords(True)

    # while True:
    #     data = wf.readframes(4000)
    #     if len(data) == 0:
    #         break
    #     if rec.AcceptWaveform(data):
    #         rec.Result()
    #         # print(rec.Result())
    #     else:
    #         rec.PartialResult()
    #         # print(rec.PartialResult())
    # # print(audio_file)
    # end = datetime.now()
    # total_time = end - start
    # print(f'Total time taken for audio file {audio_file} {total_time} ')
    # final_result = json.loads(rec.FinalResult())
    # final_result = final_result['text']+'\n'
    # # print(audio_file)
    # # print(rec.FinalResult())
    # print()
    # # print(type (rec.FinalResult()))
    # print()
    # print(final_result)
    # # print('text')
    # # print(final_result['text'])
    # print()
    # # return final_result, 200
    # return f'Results for audio file {audio_file}:\n converted text - {final_result}\n total time - {total_time}\n', 200




def initialize_model():
    global model
    model = Model(model_name="vosk-model-en-us-0.22")


if __name__ == "__main__":
    initialize_model()
    app.run(debug=True,host="0.0.0.0",port=5001)