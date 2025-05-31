from abc import ABC, abstractmethod

class login_adapter(ABC):
    @abstractmethod
    def login(self) -> dict:
        pass