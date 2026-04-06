from abc import ABC, abstractmethod

class IDrugNameExtractionService(ABC):

    @abstractmethod
    def extract(self, file):
        """
        Takes an image file and returns detected drug names.
        """
        pass