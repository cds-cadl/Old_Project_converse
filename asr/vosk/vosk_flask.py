from flask import Flask, request
import json
app = Flask(__name__)

import wave
import sys
from datetime import datetime

from vosk import Model, KaldiRecognizer, SetLogLevel

# You can set log level to -1 to disable debug messages
SetLogLevel(0)

@app.route("/get_text/<audio_file>")
def get_text(audio_file):
    AUDIO_FILE = audio_file
    wf = wave.open(AUDIO_FILE)
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        sys.exit(1)

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
        else:
            rec.PartialResult()

    end = datetime.now()
    total_time = end - start
    print(f'Total time taken for audio file {audio_file} {total_time} ')
    final_result = json.loads(rec.FinalResult())
    final_result = final_result['text']+'\n'
    print()
    print()
    print(final_result)
    print()
    return f'Results for audio file {audio_file}:\n converted text - {final_result}\n total time - {total_time}\n', 200

@app.route("/test", methods=["GET"])
def test():
    return 'hello', 200

@app.route("/get_text_from_audio", methods=["POST"])
def get_text_from_audio():
    with open('myfile.wav', mode='bw') as f:
        f.write(request.data)
    print('file written')
    text = get_text('myfile.wav')[0]
    return text[0], 200

def initialize_model():
    global model
    model = Model(model_name="vosk-model-en-us-0.22")

if __name__ == "__main__":
    initialize_model()
    app.run(debug=True,host="0.0.0.0",port=5001)