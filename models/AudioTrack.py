class AudioTrack:

    def __init__(self, language, name, trackType, features):
        self.language = language
        self.name = name
        self.trackType = trackType
        self.features = features

    def __str__(self):
        return f"[{self.name}, {self.language}]"

    def __repr__(self):
        return self.name
