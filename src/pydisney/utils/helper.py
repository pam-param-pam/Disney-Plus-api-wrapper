import json
import re
from datetime import timedelta, datetime

from ..Config import APIConfig


def rename_filename(filename):
    """Fix invalid character from title"""

    filename = (
        filename.replace(" ", ".")
        .replace("'", "")
        .replace('"', "")
        .replace(",", "")
        .replace("-", "")
        .replace(":", ".")
        .replace("’", "")
        .replace('"', '')
        .replace("-.", ".")
        .replace(".-.", ".")
    )
    filename = re.sub(" +", ".", filename)
    for _ in range(5):
        filename = re.sub(r"(\.\.)", ".", filename)
    filename = re.sub(r'[/\\:|<>"?*\0-\x1f]|^(AUX|COM[1-9]|CON|LPT[1-9]|NUL|PRN)(?![^.])|^\s|[\s.]$',
                      "", filename[:255], flags=re.IGNORECASE)

    return filename


def update_file():
    with open("token.json", "w") as file:
        current_time = datetime.now()
        expiration_time = current_time + timedelta(hours=4)
        token_data = {
            "token": APIConfig.token,
            "refresh": APIConfig.refresh,
            "expiration_time": expiration_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        json.dump(token_data, file)
