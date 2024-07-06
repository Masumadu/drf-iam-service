from core.interfaces.notifications import NotificationInterface


class Notify:
    # notification_signals = Namespace()
    # signal = notification_signals.signal("notify")

    def notify(self, notification_listener: NotificationInterface):
        self.send_notification(notification=notification_listener)

    # @signal.connect
    # noinspection PyMethodMayBeStatic
    def send_notification(self, **kwargs):
        notification = kwargs["notification"]
        notification.send()
