from abc import ABC, abstractmethod

class IView(ABC):
    @abstractmethod
    def get(self, request, u_id=None):
        pass

    @abstractmethod
    def post(self, request):
        pass

    @abstractmethod
    def put(self, request, u_id):
        pass

    @abstractmethod
    def delete(self, request, u_id):
        pass
