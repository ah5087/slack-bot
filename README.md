# Slack Onboarding Bot

## Introduction

The Slack Onboarding Bot is designed to streamline the onboarding process for new team members.

### Key Features:

- **Automated Welcome:** Automatically sends a welcome message to new team members when they join the Slack workspace.
- **Channel Assignment:** Allows users to join specific channels using emoji reactions.
- **Announcements:** Delivers important logistic information to all new members.
- **Customizable:** Easily update and customize the welcome message and information blocks.

## Demo

Here is a quick demo:

[![Slack Onboarding Bot Demo](https://img.youtube.com/vi/6ExcNBB_x_0/0.jpg)](https://www.youtube.com/watch?v=6ExcNBB_x_0&ab_channel=AliceHou)

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/slack-onboarding-bot.git
   cd slack-onboarding-bot
   ```

2. **Set up a virtual environment:**

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the environment variables:**
   Create a `.env` file and add your Slack bot token and signing secret:

   ```plaintext
   SLACK_BOT_TOKEN="######"
   SLACK_SIGNING_SECRET="######"
   ```

5. **Run the application:**

   ```bash
   python app.py
   ```

6. **Set up event subscriptions in Slack:**

   - Go to the Slack app's settings page.
   - Enable "Event Subscriptions" and set the request URL to your server's endpoint, e.g., `http://your-server.com/slack/events`.
   - Subscribe to the following bot events: `team_join`, `reaction_added`, `pin_added`, and `message`.

7. **Add the required OAuth scopes:**
   - `channels:manage`
   - `groups:write`
   - `im:write`
   - `chat:write`
   - `reactions:read`

## Usage

Once set up, the bot will automatically send a welcome message to any new user who joins the workspace. Users can react to the message with specific emojis to be added to the respective channels.
