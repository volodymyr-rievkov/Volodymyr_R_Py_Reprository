from abc import ABC, abstractmethod

class IRepository(ABC):
    
    @abstractmethod
    def show_all(self):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, id):
        pass

    @abstractmethod
    def create(self, **kwargs):
        pass

    @abstractmethod
    def update(self, object, **kwargs):
        pass
