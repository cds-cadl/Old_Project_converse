import record_voice
import requests

API_ENDPOINT = 'http://34.73.248.134:5001'

def record_and_send():
    audio_file_path = record_voice.record_to_file()
    data = open(audio_file_path, 'rb')
    headers = {'content-type': 'audio/wav'}
    r = requests.post(f'{API_ENDPOINT}/get_text_from_audio', data=data, headers=headers)
    print(r.text)
    return r.text


# if __name__ == "__main__":
#     do_continue = True

#     while do_continue:
#         choice = input("To transcribe, press 1 and record when prompted. To quit, press anything else\n")
#         if choice == '1':
#             record_and_send()
#         else:
#             do_continue = False

if __name__ == "__main__":
    do_continue = True

    choice = input("To start transcribing, press 1 and record when prompted. To stop transcribing, press anything else\n")
    if choice == '1':
        while do_continue:
            record_and_send()
