from abc import ABC, abstractmethod

class Observer(ABC):
    """
    Observer interface to be implemented by all concrete observers.
    """

    @abstractmethod
    def update(self, message):
        """
        Method to update the observer, called by the subject.

        Args:
        - message: Information sent from the subject to its observers.
        """
        pass


class Subject:
    """
    Subject to be observed. Manages and notifies its observers.
    """

    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        """
        Add an observer to the subject's list of observers.

        Args:
        - observer: The observer to be added.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """
        Remove an observer from the subject's list of observers.

        Args:
        - observer: The observer to be removed.
        """
        self._observers.remove(observer)

    def notify_observers(self, message):
        """
        Notify all observers about an event.

        Args:
        - message: Information to be passed to the observers.
        """
        for observer in self._observers:
            observer.update(message)
