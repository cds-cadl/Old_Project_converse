import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Define the URL for the Deepgram API endpoint
url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"

# Define the headers for the HTTP request
api_key = os.getenv('API_KEY') ## Use dotenv package to load the API key. Alternatively, you can copy paste your API key here everytime. NEVER UPLOAD YOUR API KEYS TO GITHUB.

headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "audio/*"
}

# Get the audio file
for i in range(1):
    # with open(f"/Users/kartikse/Documents/OS-DPI/OS-DPI/fast-api/deepgram/../audio_files/audio-stimuli/7/7.{i}.wav", "rb") as audio_file: ## Used this line inside for loop to loop through multiple audio files
    with open(f"/Users/kartikse/Documents/OS-DPI/Project-Converse/asr/vosk/audios/Daredevil.wav", "rb") as audio_file: ## Replae this path with the path to an audio file in your directory
        # Make the HTTP request
        start = datetime.now()
        response = requests.post(url, headers=headers, data=audio_file).json()

        end = datetime.now()
        total_time = end - start
        print(f'Total time taken {total_time} ')
        print()

    print()
    print(response['results']['channels'][0]['alternatives'][0]['transcript'])
    print()
    print()