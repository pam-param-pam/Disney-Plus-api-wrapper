class Caption:

    def __init__(self, language, name, trackType):
        self.language = language
        self.name = name
        self.trackType = trackType

    def __str__(self):
        return f"[{self.name}, {self.language}]"

    def __repr__(self):
        return self.name
