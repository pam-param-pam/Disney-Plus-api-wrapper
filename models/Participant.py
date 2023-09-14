class Participant:
    def __init__(self, displayName, id, sortName, order):
        self.displayName = displayName
        self.id = id
        self.sortName = sortName
        self.order = order

    def __str__(self):
        return self.displayName

    def __repr__(self):
        return self.displayName
    