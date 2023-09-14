import logging
import profile

from models.Actor import Actor
from models.AudioTrack import AudioTrack
from models.Caption import Caption
from models.HitType import HitType

from models.Participant import Participant
from models.Profile import Profile

logger = logging.getLogger('Parser')
logger.setLevel(logging.DEBUG)


def parseParticipants(participants_json):
    def extract_participants(participants_json, participant_type):
        participants = []
        try:
            for participant in participants_json.get(participant_type, []):
                displayName = participant["displayName"]
                order = participant["order"]
                id = participant["participantId"]
                sortName = participant["sortName"]
                if participant_type == "Actor":
                    character = participant["characterDetails"]["character"]
                    characterId = participant["characterDetails"]["characterId"]
                    participants.append(
                        Actor(character=character, characterId=characterId, displayName=displayName, order=order, id=id,
                              sortName=sortName))
                else:
                    participants.append(Participant(displayName=displayName, order=order, id=id, sortName=sortName))
        except KeyError:
            pass
        return participants

    actors = extract_participants(participants_json, "Actor")
    directors = extract_participants(participants_json, "Director")
    producers = extract_participants(participants_json, "Producers")
    creators = extract_participants(participants_json, "Created By")

    return actors, directors, producers, creators


def parseProfile(profile_json):
    id = profile_json["id"]
    name = profile_json["name"]
    kidsMode = profile_json["attributes"]["kidsModeEnabled"]
    isDefault = profile_json["attributes"]["isDefault"]

    prf = Profile(id=id, name=name, kidsMode=kidsMode, isDefault=isDefault)
    prf.avatar.id = profile_json["attributes"]["avatar"]["id"]
    prf.avatar.userSelected = profile_json["attributes"]["avatar"]["userSelected"]

    prf.languagePreferences.app = profile_json["attributes"]["languagePreferences"]["appLanguage"]

    prf.languagePreferences.playback = profile_json["attributes"]["languagePreferences"]["playbackLanguage"]

    prf.languagePreferences.subtitle = profile_json["attributes"]["languagePreferences"]["subtitleLanguage"]
    prf.languagePreferences.subsEnabled = profile_json["attributes"]["languagePreferences"]["subtitlesEnabled"]
    return prf


def parseHits(hits_json, search=False):
    # lazy importing to avoid circular import
    # im dumb and can't design the module structure better
    from models.Series import Series
    from models.Movie import Movie

    hits = []
    for hit_json in hits_json:

        if search:
            hit_json = hit_json["hit"]
        id = hit_json["contentId"]
        isProgram = True
        try:
            # film
            title = hit_json["text"]["title"]["full"]["program"]["default"]["content"]
        except KeyError:
            # series
            isProgram = False
            title = hit_json["text"]["title"]["full"]["series"]["default"]["content"]
        if isProgram:
            hitType = HitType.Movie
            hit = Movie(title=title, id=id, type=hitType)

            hit.internalTitle = hit_json["internalTitle"]
            hit.format = hit_json["mediaMetadata"]["format"]
            hit.mediaId = hit_json["mediaMetadata"]["mediaId"]
            hit.familyId = hit_json["family"]["familyId"]
            hit.encodedFamilyId = hit_json["family"]["encodedFamilyId"]
            hit.length = hit_json["mediaMetadata"]["runtimeMillis"]

        else:
            hitType = HitType.Series
            hit = Series(title=title, id=id, type=hitType)

            hit.seriesId = hit_json["seriesId"]
            hit.encodedSeriesId = hit_json["encodedSeriesId"]
            hit.familyId = hit_json.get(
                "familyId")  # sometimes they key is missing, but it's not that important hence the program shouldn't crash
            hit.encodedFamilyId = hit_json["family"]["encodedFamilyId"]

        hit.contentId = hit_json["contentId"]
        hit.images = hit_json["image"]
        hit.releaseType = hit_json["releases"][0]["releaseType"]
        hit.releaseDate = hit_json["releases"][0]["releaseDate"]
        hit.releaseYear = hit_json["releases"][0]["releaseYear"]
        hit.ImpliedMaturityValue = hit_json.get("ratings")[0].get(
            "impliedMaturityValue")  # sometimes they key is missing, but it's not that important hence the program shouldn't crash
        hit.rating = hit_json["ratings"][0]["value"]

        hits.append(hit)

    return hits

def parseAudioCaptions(string_json):
    audioTracks = []
    for audioTrack in string_json["mediaMetadata"]["audioTracks"]:
        features = audioTrack["features"]
        language = audioTrack["language"]
        name = audioTrack["renditionName"]
        trackType = audioTrack["trackType"]
        audioTrack = AudioTrack(features=features, name=name, language=language, trackType=trackType)
        audioTracks.append(audioTrack)

    captions = []
    for audioTrack in string_json["mediaMetadata"]["captions"]:
        language = audioTrack["language"]
        name = audioTrack["renditionName"]
        trackType = audioTrack["trackType"]
        caption = Caption(name=name, language=language, trackType=trackType)
        captions.append(caption)

    return audioTracks, captions