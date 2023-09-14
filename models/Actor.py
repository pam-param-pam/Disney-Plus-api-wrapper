class Actor:

    def __init__(self, character, characterId, displayName, id, sortName, order):
        self.character = character
        self.characterId = characterId

        self.displayName = displayName
        self.id = id
        self.sortName = sortName
        self.order = order

    def __str__(self):
        return self.displayName

    def __repr__(self):
        return self.displayName
