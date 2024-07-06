import abc


class EventHandlerInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, "handler") and callable(subclass.handler)

    @abc.abstractmethod
    def handler(self, event_data):
        """
        :param event_data: data to be processed as a result of event
        :return:
        """
        raise NotImplementedError
