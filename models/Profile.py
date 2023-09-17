from models.Avatar import Avatar
from models.LanguagePreferences import LanguagePreferences


class Profile:
    def __init__(self, profile_id, name, kids_mode, is_default):
        self.id = profile_id
        self.name = name
        self.kids_mode = kids_mode
        self.avatar = Avatar()
        self.is_default = is_default
        self.language_preferences = LanguagePreferences()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
