import openai
import config
from gtts import gTTS
import os
import random
import requests
# from pydub import AudioSegment

openai.api_key = config.OPENAI_API_KEY

# To generate AI response to prompt
def generate_response(prompt):

    # URL if using informed AI
    url = 'http://35.203.35.125:6000/generate_response_informed'

    # URL if using uninformed AI
    # url = "http://35.203.35.125:5000/generate_response"

    data = {"prompt":prompt}
    response = requests.post(url, json=data)

    return response.json()

# To convert text to speech
def generate_audio(text):

    tts = gTTS(text, lang='en-us')
    tts.save('audio.mp3')

    with open('audio.mp3', 'rb') as f:
        audio_content = f.read()

    os.remove('audio.mp3')

    return audio_content

# To transcribe speech to text
def transcribe(audio):
  
  audio_file = open(audio, "rb")
  transcript = openai.Audio.transcribe("whisper-1", audio_file,language = "en", response_format="json")

  return transcript.text

# To generate a sentence for the trainer
def generate_sentence():

    lst = ["agree", "disagree"]

    return "I " + random.choice(lst)

# To assess the user's response to trainer
def response_score(r1, r2):

    arr1, arr2 = r1.split(), r2.split()
    correct = 0

    for i in range(min(len(arr1),len(arr2))):
        if arr1[i] == arr2[i]:
            correct += 1
    
    score = round(correct/len(arr1),4) * 100

    return str(score) + "%"


