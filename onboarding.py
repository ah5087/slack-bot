class OnboardingTutorial:
    """Constructs the onboarding message and stores the state of which tasks were completed."""

    WELCOME_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Welcome to the HackPrinceton organizing team! :wave: \n\n"
                "*A couple important action items before we start:*"
            ),
        },
    }
    DIVIDER_BLOCK = {"type": "divider"}

    def __init__(self, channel):
        self.channel = channel
        self.username = "pythonboardingbot"
        self.icon_emoji = ":robot_face:"
        self.timestamp = ""
        self.reaction_task_completed = False
        self.pin_task_completed = False

    def get_message_payload(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                self.WELCOME_BLOCK,
                self.DIVIDER_BLOCK,
                *self._get_reaction_block(),
                self.DIVIDER_BLOCK,
                *self._get_logistics_block(),
                self.DIVIDER_BLOCK,
                *self._eclub_block(),
            ],
        }

    def _get_reaction_block(self):
        text = (
            "All of our team communications will be held over Slack, so please make sure your notifications are turned on! We have a separate channel set up for each team. Please react to this message to get added to your team's channel: \n"
            ":receipt: *Operations*\n"
            ":money_with_wings: *Partnerships*\n"
            ":computer: *Dev*\n"
            ":art: *Branding*\n"
            ":tada: *Experience*\n"
        )
        information = (
            ":information_source: *<https://get.slack.help/hc/en-us/articles/206870317-Emoji-reactions|"
            "Learn How to Use Emoji Reactions>*"
        )
        return self._get_task_block(text, information)
    
    def _get_logistics_block(self):
        text = (
            "*Logistics:* \n\n"
            "We will be holding *pick-ups* this Friday, September 22nd for the Entrepreneurship Club (E-Club) Mixer! :tropical_drink: Please fill out <https://docs.google.com/forms/d/e/1FAIpQLSfOzTtAt42pLSaGIWO6y0sVWO34LehYe2g3PyUFHtFBdaH3xA/viewform|this form> and be in your dorm this Friday from 8:30 - 9:30 PM! \n \n"
            "Our first all-team meeting will be next Tuesday, September 26th at 9 PM @ Frist MPR, and we're super excited to see you there! \n \n"
            "If you have any questions, please feel free to reach out to Alice via Slack or email (ah5087@princeton.edu)!"
        )
        return self._get_task_block(text)

    def _eclub_block(self):
        text = (
            "Lastly, to confirm your E-Club membership please fill out the yearly census by Sunday, September 24th. We want to get to know who our E-Club members are, what experiences they've had, and which backgrounds they hail from. This shouldn't take more than 2 minutes, and most questions are optional."
        )
        return self._get_task_block(text)

    @staticmethod
    def _get_checkmark(task_completed: bool) -> str:
        if task_completed:
            return ":white_check_mark:"
        return ":white_large_square:"

    @staticmethod
    def _get_task_block(text, information=""):
        task_block = [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}}
        ]
        if information:
            task_block.append(
                {"type": "context", "elements": [{"type": "mrkdwn", "text": information}]}
            )
        return task_block
