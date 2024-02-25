from abc import ABC, abstractmethod


class Browser(ABC):
    @abstractmethod
    def get_properties_infos(self, state, city):
        raise NotImplementedError()
