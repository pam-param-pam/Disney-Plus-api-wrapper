import logging

from ..models.Profile import Profile

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def parse_profile(profile_json):
    profile_id = profile_json["id"]
    name = profile_json["name"]
    kids_mode = profile_json["attributes"]["kidsModeEnabled"]
    is_default = profile_json["attributes"]["isDefault"]
    av_id = profile_json["attributes"]["avatar"]["id"]
    av_user_selected = profile_json["attributes"]["avatar"]["userSelected"]
    prf = Profile(profile_id=profile_id, name=name, kids_mode=kids_mode, is_default=is_default, av_id=av_id,
                  av_user_selected=av_user_selected)

    prf.language_preferences.app = profile_json["attributes"]["languagePreferences"]["appLanguage"]

    prf.language_preferences.playback = profile_json["attributes"]["languagePreferences"]["playbackLanguage"]

    prf.language_preferences.subtitle = profile_json["attributes"]["languagePreferences"]["subtitleLanguage"]
    prf.language_preferences.subs_enabled = profile_json["attributes"]["languagePreferences"]["subtitlesEnabled"]
    return prf


def find_pagination_values(data):
    """
    Recursively walks through a JSON object to find the first pagination structure and return its values.

    :param data: The JSON data (dict or list).
    :return: A JSON object containing the first pagination structure found.
    """
    pagination_keys = {"hasMore", "hasPrev", "currentOffset"}

    if isinstance(data, dict):
        # Check if current dictionary contains pagination keys
        if pagination_keys.issubset(data.keys()):
            return {
                "hasMore": data["hasMore"],
                "hasPrev": data["hasPrev"],
                "currentOffset": data["currentOffset"],
                "totalCount": data.get("totalCount")
            }

        # Recurse into each value in the dictionary
        for value in data.values():
            result = find_pagination_values(value)
            if result:
                return result

    elif isinstance(data, list):
        # Recurse into each item in the list
        for item in data:
            result = find_pagination_values(item)
            if result:
                return result

    return None


def safe_get(d, keys, default=None, ignoreError=False):
    """Safely retrieve nested dictionary keys."""
    current = d
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError) as e:
        if not ignoreError:
            logger.warning(f"Missing key: {''.join(f'[{key}]' for key in keys)}")
            # if not default:
            #     raise e
        return default


