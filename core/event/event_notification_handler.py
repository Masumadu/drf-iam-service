from core.interfaces.notifications import NotificationInterface


class EventNotificationHandler(NotificationInterface):
    """
    this class handles event notification by publishes an Event message to
    the message queue which is consumed by the rightful service.
    """

    def send(self):
        pass
