from abc import ABC, abstractmethod

class IReportView(ABC):

    @abstractmethod
    def get(self, request):
        pass
