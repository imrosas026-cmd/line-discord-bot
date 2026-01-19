from flask import Flask, request
import requests
import hmac
import hashlib
import os

app = Flask(__name__)

# Environment Variables (set these in Render)
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")

def verify_signature(body, signature):
    hash = hmac.new(
        CHANNEL_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()
    return hmac.compare_digest(hash, signature.encode("utf-8"))

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data()

    if not verify_signature(body, signature):
        return "Invalid signature", 400

    events = request.json.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_id = event["source"].get("userId", "Unknown")
            message = event["message"]["text"]

            payload = {
                "content": (
                    "📩 **LINE Message Received**\n"
                    f"User ID: {user_id}\n"
                    f"Message: {message}"
                )
            }

            requests.post(DISCORD_WEBHOOK, json=payload)

    return "OK", 200

@app.route("/")
def home():
    return "LINE → Discord bot is running"

if __name__ == "__main__":
    app.run()
