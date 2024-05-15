from openai import OpenAI

import speech_recognition as sr
from datetime import datetime

# obtain path to "english.wav" in the same folder as this script
from os import path
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "english.wav")

# use the audio file as the audio source
r = sr.Recognizer()
with sr.AudioFile(AUDIO_FILE) as source:
    audio = r.record(source)  # read the entire audio file
print ("Processing...")

print("Time taken by Google Speech Recognition")
start = datetime.now()
# recognize speech using Google Speech Recognition
try:
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
