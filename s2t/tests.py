
## check that the config parser is working
import configparser
import openai

config = configparser.ConfigParser()
config.read('./.config')

openai.api_key = config.get('OPENAI','OPENAI_API_KEY')

with open("./s2t/theSunIsUp.mp3", "rb") as audio_file:
    transcript = openai.Audio.transcribe(
        file = audio_file,
        model = "whisper-1",
        response_format="text",
        language="en"
    )
print(transcript)


## make open ai transcribe a controlled sample
