from flask import Flask, request
from slack_sdk import WebClient
import os
from google import genai

app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
client = WebClient(token=SLACK_BOT_TOKEN)

# Gemini client gets API key from GEMINI_API_KEY env variable
genai_client = genai.Client()

@app.route('/', methods=['POST','GET'])
def slack_events():
    if request.method == 'GET':
        return "Slack Bot is running", 200

    data = request.json

    # Slack URL verification challenge
    if data and data.get('type') == 'url_verification':
        return data.get('challenge'), 200

    # Handle app_mention event
    if data and 'event' in data and data['event']['type'] == 'app_mention':
        channel_id = data['event']['channel']
        text = data['event']['text']

        try:
            response = genai_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=text
            )
            answer = response.text
        except Exception as e:
            answer = f"Sorry, Gemini API error: {e}"

        client.chat_postMessage(channel=channel_id, text=answer)

    return '', 200

if __name__ == "__main__":
    app.run(port=5000)
