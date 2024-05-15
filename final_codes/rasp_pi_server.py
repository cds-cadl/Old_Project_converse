from flask import Flask
import json
import pyaudio
import asyncio
import websockets

from datetime import datetime

app = Flask(__name__)

## To test if the server is working
@app.route("/", methods=["GET"])
def test_server():
    return 'The server is working. Use /get_audio_transcription'

@app.route("/get_audio_transcription", methods=["GET"])
def get_text_from_audio():
    '''
    1. Trigger Nova.
    2. Get text from audio via Nova.
    3. Send text as a response.
    '''

    start = datetime.now()
    text = get_speech_to_text()
    end = datetime.now()
    total_time = end - start
    json_resp = {'text': text,
			'time_received': start,
			'time_processed': end,
			'total_time':total_time}
    return json.dumps(json_resp, default=str)

def get_speech_to_text():
    DEEPGRAM_API_KEY = "" ## Use dotenv package to load the API key. Alternatively, you can copy paste your API key here everytime. NEVER UPLOAD YOUR API KEYS TO GITHUB.
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 8000

    audio_queue = asyncio.Queue()

    def callback(input_data, frame_count, time_info, status_flags):
        audio_queue.put_nowait(input_data)

        return (input_data, pyaudio.paContinue)

    async def microphone(): 
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format = FORMAT,
            channels = CHANNELS,
            rate = RATE,
            input = True,
            frames_per_buffer = CHUNK,
            stream_callback = callback
        )

        stream.start_stream()

        while stream.is_active():
            await asyncio.sleep(0.1)

        stream.stop_stream()
        stream.close()

    async def process():
        extra_headers = {
            'Authorization': 'token ' + DEEPGRAM_API_KEY
        }
        
        ## Nova has many options (for example endpointing). If required, add them as URL options in this URL.
        async with websockets.connect('wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000&channels=1', extra_headers = extra_headers) as ws:
            async def sender(ws): # sends audio to websocket
                try:
                    while True:
                        data = await audio_queue.get()
                        await ws.send(data)
                except Exception as e:
                    print('Error while sending: ', + str(e))
                    raise
                
            async def receiver(ws): 
                async for msg in ws:
                    msg = json.loads(msg)
                    global transcript
                    transcript = msg['channel']['alternatives'][0]['transcript']
                    
                    if transcript:
                        print(f'Transcript = {transcript}')
                        ## The following lines are used to cancel all the async tasks so we can get the transcript and send it in `finally` ##
                        tasks = asyncio.all_tasks()
                        for task in tasks:
                            await asyncio.sleep(0)
                            task.cancel()

            await asyncio.gather(sender(ws), receiver(ws))

    async def run():
        print("SPEAK NOW")
        await asyncio.gather(microphone(),process())

    try:
        asyncio.run(run())
    except asyncio.CancelledError:
        pass
    finally:
        return transcript

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5001)
