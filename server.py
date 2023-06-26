from flask import Flask, render_template, request, jsonify
import main
import json
import base64
import os

app = Flask(__name__)
app.debug = True
app.config["TEMPLATES_AUTO_RELOAD"]  = True

# venv: env\Scripts\activate
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
    audio_file.save('request.wav')

    return 'Audio saved successfully!', 200

# Send the transcribed audio of the user prompt 
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():

    data = json.loads(request.data)
    filename = data['filename']
    transcription = main.transcribe(filename)
    os.remove(filename)

    return transcription

# Log the QuickTalker details
@app.route('/log', methods=['POST'])
def log():

    data = request.form
    main.update_log(data['time'], data['latency'], data["action"], data['prompt'], data['resp1'], data['resp2'])

    return 'Data logged successfully!', 200

# Send the text-to-speech output
@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():

    input_data = request.form['input_text']
    audio_content = main.generate_audio(input_data)

    return jsonify({'audio_content': base64.b64encode(audio_content).decode('utf-8')})

# To handle file uploads for the trainer
@app.route('/upload', methods=['POST'])
def upload():
    resp = ''
    num_lines = 0
    code = 404
    file = request.files['file']
    if file.filename != '':
        # Get the user input for the number of lines to be used
        num_lines = int(request.form['num_lines'])

        # Read the file content
        file_content = file.read().decode().splitlines()

        if num_lines == -1:
            num_lines = len(file_content)

        # Check if the number of lines requested is greater than the available lines in the file
        if num_lines > len(file_content):
            resp = 'Error: The number of prompts exceeds the available prompts in the file.'

        else:
            file.stream.seek(0)
            file.save('trainer_prompts.txt')
            main.update_header()
            code = 200
            resp = 'File uploaded successfully!'
    else:
        resp = 'No file selected.'

    return jsonify({'msg':resp, 'numPrompts':num_lines, 'code':code})

# Send the generated sentence for the trainer
@app.route('/generate-sentence', methods=['POST'])
def generate_trainer_prompt():

    lineNum = int(request.form['line'])
    return main.generate_sentence(lineNum)

# Log the Trainer details
@app.route('/log-trainer', methods=['POST'])
def logTrainer():

    data = request.form
    main.update_trainer_log(data['time'], data['latency'], data['prompt'])

    return 'Data logged successfully!', 200


# Send the user response's score for the trainer
@app.route('/score', methods=['POST'])
def score():

    prompt, resp = request.form['prompt'], request.form['resp']

    return str(main.response_score(prompt, resp)) + "%"


if __name__ == '__main__':
    app.run(debug=True)