# #!/usr/bin/env python3
# import speech_recognition as sr
from openai import OpenAI

# # # obtain audio from the microphone
# r = sr.Recognizer()
# with sr.Microphone() as source:
#  print("Say something!")
#  audio = r.listen(source)
# print ("Processing...")
# client = OpenAI()
# with open("microphone-results.wav", "wb") as f:
#  f.write(audio.get_wav_data())

# with open("microphone-results.wav", "rb") as f:
#  transcript = client.audio.transcriptions.create(
#  model="whisper-1", 
#  file=f,
#  response_format="text",
#  )
#  print(transcript)


import speech_recognition as sr
from datetime import datetime
# obtain path to "english.wav" in the same folder as this script
from os import path
# with sr.Microphone() as source:
#  print("Say something!")
#  audio = sr.Recognizer.listen(source)
# AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "english.wav")
# AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "jackhammer.wav")
# AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "harvard.wav")
# AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "4320211.mp3")
# AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "male.wav")
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "female.wav")

# 4320211
# use the audio file as the audio source
r = sr.Recognizer()
with sr.AudioFile(AUDIO_FILE) as source:
    audio = r.record(source)  # read the entire audio file
print ("Processing...")

# client = OpenAI()
# with open("microphone-results.wav", "wb") as f:
#  f.write(audio.get_wav_data())
 
# with open("microphone-results.wav", "rb") as f:
#  transcript = client.audio.transcriptions.create(
#  model="whisper-1", 
#  file=f,
#  response_format="text",
#  )
#  print(transcript)

# start = datetime.fromtimestamp(datetime.now())


print("Time taken by Google Speech Recognition")
start = datetime.now()
# recognize speech using Google Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))

end = datetime.now()
print(end - start)


print("Time taken by OpenAI Whisper")
start = datetime.now()
try:
    print(r.recognize_whisper(audio))
except sr.UnknownValueError:
    print("Did not understand")
except sr.RequestError as e:
    print(e)
# end = datetime.fromtimestamp(datetime.now())
end = datetime.now()
print(end - start)
