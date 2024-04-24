import requests
from datetime import datetime

# Define the URL for the Deepgram API endpoint
url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"

# Define the headers for the HTTP request
headers = {
    "Authorization": "Token 06a5361aee7ee3adb59616e681ea88cdf0745f22",
    "Content-Type": "audio/*"
}

# Get the audio file
for i in range(1):
    # with open(f"/Users/kartikse/Documents/OS-DPI/OS-DPI/fast-api/deepgram/../audio_files/audio-stimuli/7/7.{i}.wav", "rb") as audio_file:
    with open(f"/Users/kartikse/Documents/OS-DPI/OS-DPI/fast-api/vosk/audios/Daredevil.wav", "rb") as audio_file:
        # Make the HTTP request
        start = datetime.now()
        response = requests.post(url, headers=headers, data=audio_file).json()

        end = datetime.now()
        total_time = end - start
        print(f'Total time taken {total_time} ')
        print()

    # print(response)
    print()
    print(response['results']['channels'][0]['alternatives'][0]['transcript'])
    print()
    print()

    # main.py (python example)

# import os
# # from dotenv import load_dotenv

# from deepgram import (
#     DeepgramClient,
#     PrerecordedOptions,
#     FileSource,
# )

# # load_dotenv()

# # Path to the audio file
# AUDIO_FILE = "/Users/kartikse/Documents/OS-DPI/OS-DPI/fast-api/deepgram/../audio_files/F_0101_10y4m_1.wav"

# API_KEY = "06a5361aee7ee3adb59616e681ea88cdf0745f22"


# def main():
#     try:
#         # STEP 1 Create a Deepgram client using the API key
#         deepgram = DeepgramClient(API_KEY)

#         with open(AUDIO_FILE, "rb") as file:
#             buffer_data = file.read()

#         payload: FileSource = {
#             "buffer": buffer_data,
#         }

#         #STEP 2: Configure Deepgram options for audio analysis
#         options = PrerecordedOptions(
#             model="nova-2",
#             smart_format=True,
#         )
#         start = datetime.now()

#         # STEP 3: Call the transcribe_file method with the text payload and options
#         response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

#         end = datetime.now()
#         total_time = end - start
#         # print(f'Total time taken {total_time} ')
#         print()
#         # STEP 4: Print the response
#         print(response.to_json(indent=4))
#         print(f'Total time taken {total_time} ')

#     except Exception as e:
#         print(f"Exception: {e}")


# if __name__ == "__main__":
#     main()
