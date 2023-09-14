
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
api = DisneyAPI(email="email", password="password", proxies={}, forceLogin=True)

profileId = api.getProfiles()[0].id  # grabs the first profile's id
print(api.setActiveProfile(profileId))
print(api.getActiveProfile())

api.setLanguage(Language.Polish)  # sets language to Polish, from now all data will be returned in that language

searches = api.search("Star wars", rating=Rating.Age9Plus)
print(searches[0].title)

# checks if the search hit is a series or a movie
if searches[0].type == HitType.Series:
    # prints  s01e01's full description
    print(searches[0].getSeasons()[0].getEpisodes()[0].fullDescription)


if searches[0].type == HitType.Movie:
    print(searches[0].length) #  returns in milliseconds
    print(searches[0].cast)
    print(searches[0].audioTracks)
    print(searches[0].captions)

```





## Disclaimer

This project can only be used for educational purposes. Using this software for malicious intent is illegal, and any damages from misuse of this software will not be the responsibility of the author.

