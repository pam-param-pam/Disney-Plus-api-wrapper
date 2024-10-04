from ..models.Avatar import Avatar
from ..models.LanguagePreferences import LanguagePreferences


class Profile:
    def __init__(self, profile_id, name, kids_mode, is_default, av_id, av_user_selected):
        self.id = profile_id
        self.name = name
        self.kids_mode = kids_mode
        self.avatar = Avatar(avatar_id=av_id, user_selected=av_user_selected)
        self.is_default = is_default
        self.language_preferences = LanguagePreferences()

    def __str__(self):
        return f"Profile({self.name})"

    def __repr__(self):
        return self.name


