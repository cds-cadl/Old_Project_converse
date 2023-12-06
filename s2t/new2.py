import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source, 1)
    print("Listening....")
    audio = r.listen(source)

print(audio)
text = r.recognize_google(audio, language = 'en-IN', show_all = True )
print("I thinks you said '" + r.recognize_google(audio) + "'")
