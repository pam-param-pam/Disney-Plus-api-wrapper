from abc import ABC, abstractmethod

from models.HitType import HitType


class Hit(ABC):

    def __init__(self, title, hit_id, hit_type: HitType):
        self.title = title
        self.id = hit_id
        self.type = hit_type

        self.release_type = None
        self.release_date = None
        self.release_year = None
        self.images = None
        self.rating = None

        self._full_description = None
        self._medium_description = None
        self._brief_description = None
        self._cast = None
        self._directors = None
        self._producers = None
        self._creators = None
        self.encoded_family_id = None
        self.content_id = None

    @property
    def cast(self):
        if not self._cast:
            self._get_more_data()
        return self._cast

    @property
    def directors(self):
        if not self._directors:
            self._get_more_data()
        return self._directors

    @property
    def producers(self):
        if not self._producers:
            self._get_more_data()
        return self._producers

    @property
    def creators(self):
        if not self._creators:
            self._get_more_data()
        return self._creators

    @property
    def full_description(self):
        if not self._full_description:
            self._get_more_data()
        return self._full_description

    @property
    def medium_description(self):
        if not self._medium_description:
            self._get_more_data()
        return self._medium_description

    @property
    def brief_description(self):
        if not self._brief_description:
            self._get_more_data()
        return self._brief_description

    @abstractmethod
    def _get_more_data(self):
        pass

    def __str__(self):
        return f"[Title={self.title}, Type={self.type.value}]"

    def __repr__(self):
        return self.title
