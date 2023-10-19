class Participant:
    def __init__(self, display_name, participant_id, sort_name, order):
        self.display_name = display_name
        self.id = participant_id
        self.sort_name = sort_name
        self.order = order

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return self.display_name
    