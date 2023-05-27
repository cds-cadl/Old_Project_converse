from flask import Flask, render_template, request, jsonify
import main
import json
import base64

app = Flask(__name__)
app.debug = True
app.config["TEMPLATES_AUTO_RELOAD"]  = True

# venv: .\env\Scripts\activate
# To run: flask --app server run
# to close venv: deactivate

@app.route("/")
def index():
    return render_template("index.html")

# Send generated user response
@app.route("/prompt", methods=['POST'])
def prompt():

    input_data = request.form['input_text']

    # For informed AI
    resp = main.generate_response(input_data)["responses"]

    # For uninformed AI
    # resp = main.generate_response(input_data)

    return jsonify({'resp':resp[0], 'alt_resp':resp[1]})

# Save audio of the user prompt
@app.route('/save-audio', methods=['POST'])
def save_audio():

    audio_file = request.files['audio']
    audio_file.save('static/audio/request.wav')

    return 'Audio saved successfully!', 200

# Send the transcribed audio of the user prompt 
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():

    data = json.loads(request.data)
    filename = data['filename']
    transcription = main.transcribe('static/audio/' + filename)

    return transcription

# Send the text-to-speech output
@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():

    input_data = request.form['input_text']
    audio_content = main.generate_audio(input_data)

    return jsonify({'audio_content': base64.b64encode(audio_content).decode('utf-8')})

# Send the generated sentence for the trainer
@app.route('/generate-sentence', methods=['POST'])
def generate_trainer_prompt():

    return main.generate_sentence()

# Send the user response's score for the trainer
@app.route('/score', methods=['POST'])
def score():

    prompt, resp = request.form['prompt'], request.form['resp']

    return main.response_score(prompt, resp)


if __name__ == '__main__':
    app.run(debug=True)