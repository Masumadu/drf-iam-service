from core.interfaces.event import EventHandlerInterface


class EventSubscriptionHandler(EventHandlerInterface):
    def handler(self, data: dict):
        """
        this class handles event subscription by processing data published message queue
        which has been subscribed to by the application.
        :param data: the event data
        :return:
        """
