from abc import ABC, abstractmethod

class IView(ABC):
    
    @abstractmethod
    def get(self, request):
        pass

    @abstractmethod
    def post(self, request):
        pass
