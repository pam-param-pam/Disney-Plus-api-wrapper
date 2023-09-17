
# Disney+ API wrapper

A future rich api wrapper for Disney+ made with python




## Usage/Examples

Simple search
```python
from DisneyAPI import DisneyAPI

api = DisneyAPI(email="email", password="password")
searches = api.search("Star wars")
print(searches[0].title) # prints title of the first search hit

```
Advanced usage

```python
from DisneyAPI import DisneyAPI
from models.HitType import HitType
from models.Language import Language
from models.Rating import Rating

# forces to use disney's login api instead of cached access and refresh tokens
# sets proxies
api = DisneyAPI(email="email", password="password", proxies={}, force_login=True)

profileId = api.get_profiles()[0].id  # grabs the first profile's id
print(api.set_active_profile(profileId))
print(api.get_active_profile())

api.set_language(Language.Polish)  # sets language to Polish, from now all data will be returned in that language

searches = api.search("Star wars", rating=Rating.Age9Plus)
print(searches[0].title)

# checks if the search hit is a series or a movie
if searches[0].type == HitType.SERIES:
    # prints s01e01's full description
    print(searches[0].get_seasons()[0].get_episodes()[0].full_description)

if searches[0].type == HitType.MOVIE:
    print(searches[0].length)  # returns in milliseconds
    print(searches[0].cast)
    print(searches[0].audio_tracks)
    print(searches[0].subtitles)

```

Downloading subtitles

```python
# by default download path is downloads/
api.set_download_path("custom/downloads")
search = api.search_movies("star wars")[0]
subs = search.subtitles
for sub in subs:
    if sub.language == "pl":
        sub.download(name="name")
```
Downloading audio

```python
search = api.search_series("marvel")[0].get_seasons()[0].get_episodes()[0]
audios = search.audio_tracks
for audio in audios:
    if audio.language == "pl":
        audio.download(name="name", quality="max")  # allowed max or min, feel free to make a PR to add custom ones
```

## Disclaimer

This project can only be used for educational purposes. Using this software for malicious intent is illegal, and any damages from misuse of this software will not be the responsibility of the author.

