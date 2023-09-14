from abc import ABC, abstractmethod

from models.HitType import HitType


class Hit(ABC):

    def __init__(self, title, id, type: HitType):
        self.title = title
        self.id = id
        self.type = type

        self.releaseType = None
        self.releaseDate = None
        self.releaseYear = None
        self.ImpliedMaturityValue = None
        self.images = None
        self.rating = None

        self._fullDescription = None
        self._mediumDescription = None
        self._briefDescription = None
        self._cast = None
        self._directors = None
        self._producers = None
        self._creators = None
        self.familyId = None
        self.encodedFamilyId = None
        self.contentId = None

    @property
    def cast(self):
        if not self._cast:
            self._getMoreData()
        return self._cast

    @property
    def directors(self):
        if not self._directors:
            self._getMoreData()
        return self._directors

    @property
    def producers(self):
        if not self._producers:
            self._getMoreData()
        return self._producers

    @property
    def creators(self):
        if not self._creators:
            self._getMoreData()
        return self._creators

    @property
    def fullDescription(self):
        if not self._fullDescription:
            self._getMoreData()
        return self._fullDescription

    @property
    def mediumDescription(self):
        if not self._mediumDescription:
            self._getMoreData()
        return self._mediumDescription

    @property
    def briefDescription(self):
        if not self._briefDescription:
            self._getMoreData()
        return self._briefDescription

    @abstractmethod
    def _getMoreData(self):
        pass


    def __str__(self):
        return f"[Title={self.title}, Type={self.type.value}]"

    def __repr__(self):
        return self.title
