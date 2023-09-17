class Actor:

    def __init__(self, character, character_id, display_name, actor_id, sort_name, order):
        self.character = character
        self.character_id = character_id

        self.display_name = display_name
        self.id = actor_id
        self.sort_name = sort_name
        self.order = order

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return self.display_name
