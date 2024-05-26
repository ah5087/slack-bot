import logging
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk.web import WebClient
from onboarding import OnboardingTutorial
import ssl as ssl_lib
import certifi
from flask import Flask, request

ssl_context = ssl_lib.create_default_context(cafile=certifi.where())

flask_app = Flask(__name__)

app = App(
    token="xoxb-7187602712337-7160384541511-gkY2jrOCTMzfed2jwFGN1Vhb",
    signing_secret="9271291585d7679d7c2f90eadaf6292e"
)

# store app data in-memory
onboarding_tutorials_sent = {}

# map of emojis to channels
emoji_to_channel = {
    "receipt": "C074QB3CSLF",  # operations
    "money_with_wings": "C0754Q7JB6F",  # partnerships
    "computer": "C075TMF6L00",  # dev
    "art": "C075HHQMBCH",  # branding
    "tada": "C0754TJ4LRG",  # experience
}

# Function to start onboarding
def start_onboarding(user_id: str, channel: str, client: WebClient):
    # create new onboarding tutorial
    onboarding_tutorial = OnboardingTutorial(channel)

    # Get the onboarding message payload
    message = onboarding_tutorial.get_message_payload()

    # post the onboarding message
    response = client.chat_postMessage(**message)

    # capture timestamp of the message
    onboarding_tutorial.timestamp = response["ts"]

    # store message sent in onboarding_tutorials_sent
    if channel not in onboarding_tutorials_sent:
        onboarding_tutorials_sent[channel] = {}
    onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial

# ================ Team Join Event =============== #
@app.event("team_join")
def onboarding_message(event, client):
    """Create and send an onboarding welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    """
    # get id of user
    user_id = event.get("user", {}).get("id")

    # open DM with new user
    response = client.conversations_open(users=user_id)
    channel = response["channel"]["id"]

    # post onboarding message
    start_onboarding(user_id, channel, client)

# ============= Reaction Added Events ============= #
@app.event("reaction_added")
def handle_reaction(event, client):
    """Handle reaction added events to add users to specific channels based on emoji."""
    user_id = event.get("user")
    reaction = event.get("reaction")

    # debug
    logging.debug(f"Received reaction: {reaction} from user: {user_id}")

    # check if the reaction emoji is in mapping
    if reaction in emoji_to_channel:
        channel_id = emoji_to_channel[reaction]
        logging.debug(f"Adding user {user_id} to channel {channel_id} for reaction {reaction}")
        add_user_to_channel(client, user_id, channel_id)
    else:
        logging.debug(f"Reaction {reaction} not found in emoji_to_channel mapping")

    # Update onboarding message for the user if applicable
    channel_id = event.get("item", {}).get("channel")
    if channel_id in onboarding_tutorials_sent and user_id in onboarding_tutorials_sent[channel_id]:
        # get original tutorial sent
        onboarding_tutorial = onboarding_tutorials_sent[channel_id][user_id]

        # mark the reaction task completed
        onboarding_tutorial.reaction_task_completed = True

        # get new message payload
        message = onboarding_tutorial.get_message_payload()

        # post updated message
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
    # get the ids of the user and channel
    channel_id = event.get("channel_id")
    user_id = event.get("user")

    if channel_id not in onboarding_tutorials_sent:
        return

    # get original tutorial
    onboarding_tutorial = onboarding_tutorials_sent[channel_id].get(user_id)

    if not onboarding_tutorial:
        return

    # mark task completed
    onboarding_tutorial.pin_task_completed = True

    # new message payload
    message = onboarding_tutorial.get_message_payload()

    # post in slack
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

handler = SlackRequestHandler(app)

# route to handle Slack events + challenge verification
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# run app
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    flask_app.run(host='0.0.0.0', port=3000)
