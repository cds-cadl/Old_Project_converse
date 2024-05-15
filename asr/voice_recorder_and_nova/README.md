# This module works in the following way.

## SETUP

1. Run mock_fin3.py. It is not a Flask server. It is acting as a client to send a command to the server to record voice.
2. Run mock_rasp_pi_server.py. This is a flask server and runs on http://localhost:5002.

record_voice.py is the module we are using to actually record the voice.

## USE

1. In the tab where you are running mock_fin3.py, whenever you want to start recording press '1'.
2. This tells the server to trigger the voice_recording module.
3. Start speaking in the mic. The program will wait for about 1 second of silence before it stops recording.
4. The recorded sound is saved in the file 'recorded_voice.wav'.
5. The server then sends this audio file to Nova, gets the text, and sends it back to the client.