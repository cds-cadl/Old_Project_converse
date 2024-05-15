from flask import Flask
app = Flask(__name__)
    
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import record_voice as record_voice

load_dotenv()

# Define the URL for the Deepgram API endpoint
url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"

# Define the headers for the HTTP request
api_key = os.getenv('API_KEY') ## Use dotenv package to load the API key. Alternatively, you can copy paste your API key here everytime. NEVER UPLOAD YOUR API KEYS TO GITHUB.

headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "audio/*"
}

def get_text(audio_file):
    with open(f"demo.recorded_voice", "rb") as audio_file:
        start = datetime.now()
        # Make the HTTP request
        response = requests.post(url, headers=headers, data=audio_file).json()

        end = datetime.now()
        total_time = end - start
        print(f'Total time taken {total_time} ')
        print()

    print()
    text = response['results']['channels'][0]['alternatives'][0]['transcript']
    print(text)
    print()
    return text

@app.route("/test", methods=["GET"])
def test():
    return 'hello', 200

@app.route("/get_audio_transcription", methods=["GET"])
def get_text_from_audio():
    audio_file_path = record_voice.record_to_file()
    start = datetime.now()
    print(audio_file_path)
    print('file written')
    text = get_text('recorded_voice.wav')
    end = datetime.now()
    print(end - start)
    return text

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5002)