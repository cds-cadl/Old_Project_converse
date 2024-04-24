from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import json
import logging
import uvicorn
import csv
from concurrent.futures import ThreadPoolExecutor
import requests
import asyncio
import speech_recognition as sr

# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)




executor = ThreadPoolExecutor(max_workers=10)
api_url = "http://35.203.35.125:7000/generate_response_informed"
headers = {"Content-Type": "application/json"}

# In-memory history of the conversation (last 3 prompts and responses)
conversation_history = []
csv_file_path = 'conversation_history.csv'
full_conversation_history = []

def get_speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, 1)
        print("Listening....")
        audio = recognizer.listen(source)

    try:
        # Recognize speech using Google Web Speech API
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        # Handle errors or unknown values
        print("Google Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        # API was unreachable or unresponsive
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        try:
            data_json = json.loads(data)
            print(data_json)
            state = data_json.get("state", {})
            prefix = state.get("$prefix", "")

            if prefix == 'prompt':
                prompt = get_speech_to_text()
                message = json.dumps({'state':{"$Display": prompt}})
                await websocket.send_text(message)
               
                if prompt:
                    logging.info(f"Received prompt: {prompt}")
                    loop = asyncio.get_running_loop()

                    # Prepare the full prompt by concatenating the last 3 history pairs with the new prompt
                    full_prompt = "\n".join(["\n".join(pair) for pair in conversation_history[-3:]]) + "\n" + prompt
                    print(full_prompt)
                    logging.info(f"Sending full prompt to model: {full_prompt}")
                    response = await loop.run_in_executor(executor, send_to_api_sync, full_prompt)

                    # Assuming 'responses' is a key in the JSON data that contains the list you're interested in
                    responses_list = response.get('responses', [])

                    # Now create your dictionary
                    responses_dict = {f"response{i+1}": resp for i, resp in enumerate(responses_list)}
                    responses_dict['Display'] = prompt
                    print(responses_dict)
                    await websocket.send_text(json.dumps(responses_dict))

                    # Update the conversation history with the prompt and placeholder for the user's chosen response
                    update_history(conversation_history, prompt, None, response, full_conversation_history)
                else:
                    logging.error("No prompt found in the received data.")

            elif prefix == 'Chosen':
                chosen_response = state.get("$socket", "")
                if chosen_response:
                    logging.info(f"Received chosen response: {chosen_response}")
                    # Update the last entry in the conversation history with the chosen response
                    if conversation_history and conversation_history[-1][1] is None:
                        conversation_history[-1] = (conversation_history[-1][0], chosen_response)
                        update_full_history(full_conversation_history, conversation_history[-1], chosen_response)
                    else:
                        logging.error("Chosen response received without a corresponding prompt.")
                else:
                    logging.error("No chosen response found in the received data.")


            else:
                logging.error(f"Unexpected prefix value: {prefix}")

        except json.JSONDecodeError:
            logging.error("Invalid JSON received.")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


def update_history(history, partner_prompt, user_response, model_responses, full_history):
    history_snapshot = history[-3:]
    # Trim the history to only keep the last 3 conversation pairs
    while len(history) > 3:
        history.pop(0)

    # Update the in-memory history with the partner's prompt and a placeholder for the user's response
    history.append((partner_prompt, user_response))

    # Update the full conversation history with the new conversation pair and model responses
    if model_responses is not None:
        full_history.append((partner_prompt, model_responses, user_response, history_snapshot))


def update_full_history(full_history, last_convo_pair, chosen_response):
    # Find the last conversation pair in the full history and update it with the chosen response
    for index, (partner_prompt, model_responses, user_response, history_snapshot) in enumerate(full_history):
        if partner_prompt == last_convo_pair[0] and user_response is None:
            full_history[index] = (partner_prompt, model_responses, chosen_response, history_snapshot)
            break



@app.get("/download_csv")
async def download_csv():
    csv_file_path = "path_to_your_csv_file.csv"  # Replace with your actual CSV file path

    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the CSV header
            writer.writerow(['index', 'prompt', 'history', 'responses', 'chosen_response'])

            # Log the length of the full conversation history
            logging.info(f"Writing CSV for {len(full_conversation_history)} conversation pairs.")

            # Write the conversation history data
            for index, (partner_prompt, model_responses, user_response, history_snapshot) in enumerate(full_conversation_history, start=1):
                # Log the current index and type of each part of the conversation pair
                logging.info(f"Writing index {index}")
                logging.info(f"Prompt: {partner_prompt}, Type: {type(partner_prompt)}")
                logging.info(f"Model Responses: {model_responses}, Type: {type(model_responses)}")
                logging.info(f"User Response: {user_response}, Type: {type(user_response)}")
                logging.info(f"History Snapshot: {history_snapshot}, Type: {type(history_snapshot)}")

                
                responses_list = model_responses.get('responses', [])
                history_str = ";\n".join(["\n".join(map(str, pair)) for pair in (history_snapshot or [])])
                responses_str = ';\n'.join(map(str, responses_list))
                writer.writerow([str(index), str(partner_prompt), history_str, responses_str, str(user_response)])

        # After generating, return the file
        return FileResponse(csv_file_path, media_type='text/csv', filename='conversation_history.csv')

    except Exception as e:
        logging.error(f"Failed to write CSV: {e}")
        return {"error": f"Failed to generate CSV: {e}"}



def send_to_api_sync(prompt):
    try:
        response = requests.post(api_url, headers=headers, json={'prompt': prompt})
        response.raise_for_status()
        print(response)
        return response.json()
    except requests.HTTPError as e:
        logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        return []
    except requests.RequestException as e:
        logging.error(f"Error sending request to API: {e}")
        return []

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5678, log_level="info")
