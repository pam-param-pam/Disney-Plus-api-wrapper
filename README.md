
# Disney+ API wrapper

A feature rich API wrapper for Disney+ made with python. 

Allows for audio and subtitle download!


## How to install
    pip install pydisney

https://pypi.org/project/pydisney

## Usage/Examples

### Simple search
```python
from pydisney import DisneyAPI

api = DisneyAPI(email="email", password="password")
searches = api.search("Star wars")
print(searches[0].title) # prints title of the first search hit
```
### More examples

```python
from pydisney import DisneyAPI
from pydisney.models.Language import Language

# forces to use disney's login api instead of cached access and refresh tokens
api = DisneyAPI(email="email", password="password", force_login=True)

profile = api.get_profiles()[0]  # grabs the first profile
print(api.set_active_profile(profile.id)) # if profile is locked, pass pin as an argument
active_profile = api.get_active_profile()
active_profile.set_profile_language(Language.English_UK) # sets language to english, from now all data will be returned in that language


searches = api.search("Star wars")
print(searches[0].title)

# checks if the search hit is a series or a movie
if searches[0].is_movie:
    print(searches[0].length)  # returns in milliseconds
    print(searches[0].credits)  # gets cast, directors etc

else:
    # prints s01e01's full description
    print(searches[0].seasons[0].episodes[0].full_description)
```

### Download Audio and Subtitles
> [!WARNING]  
> Audio download requires `ffmpeg` installed and available in PATH.

```python
from pydisney import DisneyAPI

episode = api.search("Andor")[0].seasons[0].episodes[0]
selector = episode.get_track_selector()

print(selector.available_languages())

audio_group = selector.get_audios(language="pl")
best_audio = audio_group.filter_by_codec("eac").get_best_quality().download() # codec: eac or aac
best_audio.download()

sub = selector.get_subtitles("pl").get_forced().first()
sub.download("subtitle-name.vtt") # pass file name if you want. Subtitles are ALWAYS in vtt format
```

Docs? What docs, read the source code. 😎

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## Disclaimer

This project can only be used for educational purposes. Using this software for malicious intent is illegal, and any damages from misuse of this software will not be the responsibility of the author.

## License

[MIT](https://choosealicense.com/licenses/mit/)
