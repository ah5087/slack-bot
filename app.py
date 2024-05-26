import logging
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk.web import WebClient
from onboarding import OnboardingTutorial
import ssl as ssl_lib
import certifi
from flask import Flask, request

# Set up SSL context
ssl_context = ssl_lib.create_default_context(cafile=certifi.where())

# Initialize Flask app
flask_app = Flask(__name__)

# Create a Bolt for Python application
app = App(
    token="xoxb-7187602712337-7160384541511-gkY2jrOCTMzfed2jwFGN1Vhb",
    signing_secret="9271291585d7679d7c2f90eadaf6292e"
)

# Store app data in-memory
onboarding_tutorials_sent = {}

# Mapping of emojis to channels
emoji_to_channel = {
    "receipt": "C074QB3CSLF",  # operations
    "money_with_wings": "C0754Q7JB6F",  # partnerships
    "computer": "C075TMF6L00",  # dev
    "art": "C075HHQMBCH",  # branding
    "tada": "C0754TJ4LRG",  # experience
}

# Function to start onboarding
def start_onboarding(user_id: str, channel: str, client: WebClient):
    # Create a new onboarding tutorial.
    onboarding_tutorial = OnboardingTutorial(channel)

    # Get the onboarding message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the onboarding message in Slack
    response = client.chat_postMessage(**message)

    # Capture the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an onboarding task.
    onboarding_tutorial.timestamp = response["ts"]

    # Store the message sent in onboarding_tutorials_sent
    if channel not in onboarding_tutorials_sent:
        onboarding_tutorials_sent[channel] = {}
    onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial

# ================ Team Join Event =============== #
@app.event("team_join")
def onboarding_message(event, client):
    """Create and send an onboarding welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    """
    # Get the id of the Slack user associated with the incoming event
    user_id = event.get("user", {}).get("id")

    # Open a DM with the new user.
    response = client.conversations_open(users=user_id)
    channel = response["channel"]["id"]

    # Post the onboarding message.
    start_onboarding(user_id, channel, client)

# ============= Reaction Added Events ============= #
@app.event("reaction_added")
def handle_reaction(event, client):
    """Handle reaction added events to add users to specific channels based on emoji."""
    user_id = event.get("user")
    reaction = event.get("reaction")

    # Debug logging
    logging.debug(f"Received reaction: {reaction} from user: {user_id}")

    # Check if the reaction emoji is in our mapping
    if reaction in emoji_to_channel:
        channel_id = emoji_to_channel[reaction]
        logging.debug(f"Adding user {user_id} to channel {channel_id} for reaction {reaction}")
        add_user_to_channel(client, user_id, channel_id)
    else:
        logging.debug(f"Reaction {reaction} not found in emoji_to_channel mapping")

    # Update onboarding message for the user if applicable
    channel_id = event.get("item", {}).get("channel")
    if channel_id in onboarding_tutorials_sent and user_id in onboarding_tutorials_sent[channel_id]:
        # Get the original tutorial sent.
        onboarding_tutorial = onboarding_tutorials_sent[channel_id][user_id]

        # Mark the reaction task as completed.
        onboarding_tutorial.reaction_task_completed = True

        # Get the new message payload
        message = onboarding_tutorial.get_message_payload()

        # Post the updated message in Slack
        updated_message = client.chat_update(**message)

# Function to add user to a channel
def add_user_to_channel(client: WebClient, user_id: str, channel_id: str):
    try:
        response = client.conversations_invite(
            channel=channel_id,
            users=user_id
        )
        logging.debug(f"User {user_id} added to channel {channel_id}: {response}")
    except Exception as e:
        logging.error(f"Error adding user to channel: {e}")

# =============== Pin Added Events ================ #
@app.event("pin_added")
def update_pin(event, client):
    """Update the onboarding welcome message after receiving a "pin_added"
    event from Slack. Update timestamp for welcome message as well.
    """
    # Get the ids of the Slack user and channel associated with the incoming event
    channel_id = event.get("channel_id")
    user_id = event.get("user")

    if channel_id not in onboarding_tutorials_sent:
        return

    # Get the original tutorial sent.
    onboarding_tutorial = onboarding_tutorials_sent[channel_id].get(user_id)

    if not onboarding_tutorial:
        return

    # Mark the pin task as completed.
    onboarding_tutorial.pin_task_completed = True

    # Get the new message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the updated message in Slack
    updated_message = client.chat_update(**message)

# ============== Message Events ============= #
@app.event("message")
def message(event, client):
    """Display the onboarding welcome message after receiving a message
    that contains "start".
    """
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if text and text.lower() == "start":
        return start_onboarding(user_id, channel_id, client)

# SlackRequestHandler to handle requests
handler = SlackRequestHandler(app)

# Route to handle Slack events and challenge verification
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# Run the app
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    flask_app.run(host='0.0.0.0', port=3000)
