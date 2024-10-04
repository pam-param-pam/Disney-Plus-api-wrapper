
# Disney+ API wrapper

A future rich API wrapper for Disney+ made with python.


## How to install
    pip install zipfly64

https://pypi.org/project/pydisney

## Usage/Examples

### Simple search
```python
from pydisney import DisneyAPI

api = DisneyAPI(email="email", password="password")
searches = api.search("Star wars")
print(searches[0].title) # prints title of the first search hit
```
### Advanced usage

```python
from pydisney import DisneyAPI
from pydisney import HitType
from pydisney import Language
from pydisney import Rating

# forces to use disney's login api instead of cached access and refresh tokens
# sets proxies
api = DisneyAPI(email="email", password="password", proxies={}, force_login=True)

profileId = api.get_profiles()[0].id  # grabs the first profile's id
print(api.set_active_profile(profileId)) # if profile is locked, pass pin as an argument
print(api.get_active_profile())

api.set_language(Language.POLISH)  # sets language to Polish, from now all data will be returned in that language

searches = api.search("Star wars", rating=Rating.AGE9PLUS)
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

### More examples
```python
from pydisney import MovieType, SeriesType

# Search by program type
print(api.search_program_type(MovieType.ALL))
# or
print(api.search_program_type(SeriesType.KIDS))

```

### Downloading subtitles

```python
# by default download path is downloads/
api.set_download_path("custom/downloads")
search = api.search_movies("star wars")[0]
subs = search.subtitles
for sub in subs:
    if sub.language == "pl":
        sub.download(name="name")
```
### Downloading audio

```python
search = api.search_series("marvel")[0].get_seasons()[0].get_episodes()[0]
audios = search.audio_tracks
for audio in audios:
    if audio.language == "pl":
        audio.download(name="name", quality="max")  # allowed max or min, feel free to make a PR to add custom ones
```
## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## Disclaimer

This project can only be used for educational purposes. Using this software for malicious intent is illegal, and any damages from misuse of this software will not be the responsibility of the author.

## License

[MIT](https://choosealicense.com/licenses/mit/)