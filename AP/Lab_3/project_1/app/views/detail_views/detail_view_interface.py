from abc import ABC, abstractmethod

class IDetailView(ABC):

    @abstractmethod
    def get(self, request, id):
        pass

    @abstractmethod
    def put(self, request, id):
        pass

    @abstractmethod
    def delete(self, request, id):
        pass
