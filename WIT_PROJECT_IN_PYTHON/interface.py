from abc import ABC, abstractmethod


class IVersionControl(ABC):
    @abstractmethod
    def init(self): pass

    @abstractmethod
    def add(self, path): pass

    @abstractmethod
    def commit(self, message): pass

    @abstractmethod
    def status(self): pass

    @abstractmethod
    def checkout(self, commit_id): pass