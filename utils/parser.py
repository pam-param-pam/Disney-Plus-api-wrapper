import logging

from models.Actor import Actor
from models.AudioTrack import AudioTrack
from models.HitType import HitType

from models.Participant import Participant
from models.Profile import Profile
from models.Subtitles import Subtitles

logger = logging.getLogger('Parser')
logger.setLevel(logging.DEBUG)


def parse_participants(participants_json):
    def extract_participants(participants_json, participant_type):
        participants = []
        try:
            for participant in participants_json.get(participant_type, []):
                display_name = participant["displayName"]
                order = participant["order"]
                participant_id = participant["participantId"]
                sort_name = participant["sortName"]
                if participant_type == "Actor":
                    character = participant["characterDetails"]["character"]
                    character_id = participant["characterDetails"]["characterId"]
                    participants.append(
                        Actor(character=character, character_id=character_id, display_name=display_name, order=order, actor_id=participant_id,
                              sort_name=sort_name))
                else:
                    participants.append(Participant(display_name=display_name, order=order, participant_id=participant_id, sort_name=sort_name))
        except KeyError:
            pass
        return participants

    actors = extract_participants(participants_json, "Actor")
    directors = extract_participants(participants_json, "Director")
    producers = extract_participants(participants_json, "Producers")
    creators = extract_participants(participants_json, "Created By")

    return actors, directors, producers, creators


def parse_profile(profile_json):
    profile_id = profile_json["id"]
    name = profile_json["name"]
    kids_mode = profile_json["attributes"]["kidsModeEnabled"]
    is_default = profile_json["attributes"]["isDefault"]

    prf = Profile(profile_id=profile_id, name=name, kids_mode=kids_mode, is_default=is_default)
    prf.avatar.id = profile_json["attributes"]["avatar"]["id"]
    prf.avatar.user_selected = profile_json["attributes"]["avatar"]["userSelected"]

    prf.language_preferences.app = profile_json["attributes"]["languagePreferences"]["appLanguage"]

    prf.language_preferences.playback = profile_json["attributes"]["languagePreferences"]["playbackLanguage"]

    prf.language_preferences.subtitle = profile_json["attributes"]["languagePreferences"]["subtitleLanguage"]
    prf.language_preferences.subs_enabled = profile_json["attributes"]["languagePreferences"]["subtitlesEnabled"]
    return prf


def parse_hits(hits_json, search=False):
    # lazy importing to avoid circular import
    # im dumb and can't design the module structure better
    from models.Series import Series
    from models.Movie import Movie

    hits = []
    for hit_json in hits_json:
        if search:
            hit_json = hit_json["hit"]
        contentId = hit_json["contentId"]
        is_program = True
        try:
            # film
            title = hit_json["text"]["title"]["full"]["program"]["default"]["content"]
        except KeyError:
            # series
            is_program = False
            title = hit_json["text"]["title"]["full"]["series"]["default"]["content"]
        if is_program:
            hit_type = HitType.MOVIE
            hit = Movie(title=title, movie_id=contentId, hit_type=hit_type)

            hit.internal_title = hit_json["internalTitle"]
            hit.format = hit_json["mediaMetadata"]["format"]
            hit.media_id = hit_json["mediaMetadata"]["mediaId"]
            hit.family_id = hit_json["family"]["familyId"]
            hit.encoded_family_id = hit_json["family"]["encodedFamilyId"]
            hit.length = hit_json["mediaMetadata"]["runtimeMillis"]

        else:
            hit_type = HitType.SERIES
            hit = Series(title=title, series_id=contentId, hit_type=hit_type)

            hit.series_id = hit_json["seriesId"]
            hit.encoded_series_id = hit_json["encodedSeriesId"]
            hit.family_id = hit_json.get(
                "familyId")  # sometimes they key is missing, but it's not that important hence the program shouldn't crash
            hit.encoded_family_id = hit_json["family"]["encodedFamilyId"]

        hit.content_id = hit_json["contentId"]
        hit.images = hit_json["image"]
        hit.release_type = hit_json["releases"][0]["releaseType"]
        hit.release_date = hit_json["releases"][0]["releaseDate"]
        hit.release_year = hit_json["releases"][0]["releaseYear"]
        hit.implied_maturity_value = hit_json.get("ratings")[0].get(
            "impliedMaturityValue")  # sometimes they key is missing, but it's not that important hence the program shouldn't crash
        hit.rating = hit_json["ratings"][0]["value"]

        hits.append(hit)

    return hits

def parse_audio_and_subtitles(string_json, media_id):
    audio_tracks = []
    for audio_track in string_json["mediaMetadata"]["audioTracks"]:
        features = audio_track["features"]
        language = audio_track["language"]
        name = audio_track["renditionName"]
        track_type = audio_track["trackType"]
        audio_track = AudioTrack(features=features, name=name, media_id=media_id, language=language, track_type=track_type)
        audio_tracks.append(audio_track)

    subtitles = []
    for audio_track in string_json["mediaMetadata"]["captions"]:
        language = audio_track["language"]
        name = audio_track["renditionName"]
        track_type = audio_track["trackType"]
        subtitle = Subtitles(name=name, language=language, media_id=media_id, track_type=track_type)
        subtitles.append(subtitle)

    return audio_tracks, subtitles
