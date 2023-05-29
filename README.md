# Project-Converse

A training tool for research in the development of conversant augmentative communication systems, to monitor responses from individuals with complex communication needs (ALS, cerebral palsy, autism).

## How to Run:
* **Prerequisite**: Python (3.4 or above)
* Clone the repo in a directory or create a directory and download the files manually in it. 
* In the terminal of that directory, run the command: **python -m venv env**
* Activate the virtual environment:
  * For Windows users, run the command: **env\Scripts\activate**
  * For macOS/Linux users, run the command: **source env/bin/activate**
* Now run the command: **pip install -r requirements.txt**
* Add a file in the directory called *'config.py'* and paste the following text with your OpenAI API key:
  * OPENAI_API_KEY = "YOUR OPENAI API KEY"  
* To run the server: **flask --app server run**
* Go to the link mentioned in the terminal output (most likely http://127.0.0.1:5000)
* To exit flask server, press *Ctrl^C* (Windows) or *Command^C* (Mac).
* Exit the virtual environment with the command: **deactivate**


## QuickTalker usage
* Type or record prompt to the Chatbot.
* To record, press the ***'r'*** key twice. To stop recording press the ***'s'*** key twice.
* To generate AI response, press ***'Enter'*** key.
* To play the first AI response as audio, press the ***'1'*** key.
* To play the second AI response as audio, press the ***'2'*** key.
* To clear the screen, press the ***'c'*** key twice. 

## Trainer Usage
* Click on ***'Generate'*** to receive a user prompt.
* From the given list of words, enter any combination of words.
* Press the ***'send'*** icon to get the score.
* The score is a comparison between the generated prompt and user's response to it. 
