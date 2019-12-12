from datetime import datetime as dt
import logging
from logging.handlers import RotatingFileHandler
import os

import requests
from bs4 import BeautifulSoup
from slate_utils.session import get_external_session
from logger.messenger import SlackMessenger

import config

if not os.path.exists('logs'):
    os.mkdir('logs')
logger = logging.getLogger(__name__)
timed_handler = RotatingFileHandler('logs/errors.log', maxBytes=10240)
timed_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s"))
timed_handler.setLevel(logging.INFO)
logger.addHandler(timed_handler)
logger.setLevel(logging.INFO)

def main():
    messenger = SlackMessenger(config.SLACK_URL)
    session = get_external_session(config.HOST, config.USERNAME, config.PASSWORD)
    r = session.get(f"{config.HOST}{config.ENDPOINT}")
    r.raise_for_status()
    soup = BeautifulSoup(r.text)
    for tr in soup.select("#responsesContainer tbody tr"):
        dttmstr, *_, msg = [td.text for td in tr.select("td")]
        logger.info(f"{dttmstr} {msg}")
        dttm = dt.strptime(dttmstr, "%m/%d/%Y %I:%M %p")
        delta = (dt.now() - dttm).seconds
        if delta // 60 <= config.STALENESS:
            messenger.add_error(dttm=dttm, msg=msg.strip())

    if messenger.errors:
        messenger.emit()


if __name__ == "__main__":
    main()
