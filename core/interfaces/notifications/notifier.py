from django.dispatch import Signal, receiver

from .notification_interface import NotificationInterface


class Notifier:
    notification_signal = Signal()

    def notify(self, notification_listener: NotificationInterface):
        self.notification_signal.send(sender=notification_listener)

    # noinspection PyMethodMayBeStatic
    @staticmethod
    @receiver(notification_signal)
    def send_notification(sender, **kwargs):
        sender.send()
