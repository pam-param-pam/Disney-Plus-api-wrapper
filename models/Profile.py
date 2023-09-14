from models.Avatar import Avatar
from models.LanguagePreferences import LanguagePreferences


class Profile:
    def __init__(self, id, name, kidsMode, isDefault):
        self.id = id
        self.name = name
        self.kidsMode = kidsMode
        self.avatar = Avatar()
        self.isDefault = isDefault
        self.languagePreferences = LanguagePreferences()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
