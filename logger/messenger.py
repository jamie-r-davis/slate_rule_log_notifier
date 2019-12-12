import requests


class SlackMessenger:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self._errors = []

    @property
    def errors(self):
        return self._errors

    def add_error(self, dttm, msg):
        self.errors.append({"dttm": dttm, "msg": msg})

    @property
    def msg(self):
        msg = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Rule Error Log Monitor*\n\nWe've got problems...",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Errors have been detected in the rule error log:",
                    },
                },
                {"type": "divider"},
            ]
        }
        for error in self.errors:
            section = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{error['dttm'].strftime('%m/%d/%Y %I:%M %p')}*\n{error['msg']}",
                },
            }
            msg["blocks"].append(section)
        return msg

    def emit(self):
        requests.post(self.webhook_url, json=self.msg)
