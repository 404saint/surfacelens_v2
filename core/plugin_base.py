from abc import ABC, abstractmethod

class IntelligenceModule(ABC):
    """
    The base class for all SurfaceLens V2 modules.
    Every module must implement these methods.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The display name of the module."""
        pass

    @abstractmethod
    def run(self, asset: dict) -> dict:
        """
        Takes an asset dictionary, performs analysis, 
        and returns a dictionary of findings.
        """
        pass