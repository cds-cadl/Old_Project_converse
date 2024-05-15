import requests

api_url_rasp_pi_server = 'http://localhost:5001'

def get_speech_to_text():
    req = requests.get(f'{api_url_rasp_pi_server}/get_audio_transcription')
    print(req)
    return



if __name__ == "__main__":
    do_continue = True

    while do_continue:
        choice = input("To transcribe, press 1 and record when prompted. To quit, press anything else\n")
        if choice == '1':
            get_speech_to_text()
        else:
            do_continue = False
