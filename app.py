from datetime import datetime as dt
import requests
from bs4 import BeautifulSoup
from slate_utils.session import get_external_session
from logger.messenger import SlackMessenger

import config


def main():
    messenger = SlackMessenger(config.SLACK_URL)
    session = get_external_session(config.HOST, config.USERNAME, config.PASSWORD)
    r = session.get(f"{config.HOST}{config.ENDPOINT}")
    r.raise_for_status()
    soup = BeautifulSoup(r.text)
    for tr in soup.select("#responsesContainer tbody tr"):
        dttmstr, *_, msg = [td.text for td in tr.select("td")]
        dttm = dt.strptime(dttmstr, "%m/%d/%Y %I:%M %p")
        delta = (dt.now() - dttm).seconds
        if delta // 60 <= config.STALENESS:
            messenger.add_error(dttm=dttm, msg=msg.strip())

    if messenger.errors:
        messenger.emit()


if __name__ == "__main__":
    main()
