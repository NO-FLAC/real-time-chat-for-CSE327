from asgiref.sync import async_to_sync
from abc import ABC, abstractmethod
class Subject(ABC):
    @abstractmethod
    def attach(self, observer_channel):
        pass

    @abstractmethod
    def detach(self, observer_channel):
        pass

    @abstractmethod
    def notify(self):
        pass

class ConcreteSubject(Subject):
    def __init__(self):
        self._observers = set()

    def attach(self, observer_channel):
        self._observers.add(observer_channel)

    def detach(self, observer_channel):
        self._observers.discard(observer_channel)

    def notify(self, event, channel_layer, group_name):
        async_to_sync(channel_layer.group_send)(group_name, event)
