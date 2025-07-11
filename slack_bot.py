from flask import Flask, request
from slack_sdk import WebClient
import requests
import os


app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
GEMINI_API_TOKEN = os.environ.get("GEMINI_API_TOKEN")

client = WebClient(token=SLACK_BOT_TOKEN)

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GEMINI_API_TOKEN}"
}

@app.route('/', methods=['POST','GET'])
def slack_events():

    if request.method == 'GET':
        return "Slack Bot is running", 200
    print(request)
    data = request.json

    # Slack URL verification challenge
    if data and data.get('type') == 'url_verification':
        print("URL,verification "+ data.get('challenge'))
        return data.get('challenge'),200

    # Handle app_mention event
    if data and 'event' in data and data['event']['type'] == 'app_mention':
        channel_id = data['event']['channel']
        text = data['event']['text']

        # Optionally, remove bot mention from text
        # text = text.replace(f"<@{your_bot_user_id}>", "").strip()

        # Prepare payload
        payload = {
            "contents": [
                {"parts": [{"text": text}]}
            ]
        }
        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()
        try:
            answer = response_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            answer = "Sorry, I couldn't get a response from Gemini."


        # Post the result back to Slack channel
        client.chat_postMessage(channel=channel_id, text=answer)

    return '', 200

if __name__ == "__main__":
    app.run(port=5000)
