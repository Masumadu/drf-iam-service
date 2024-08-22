from django.dispatch import Signal

tester = Signal()


# @receiver(tester)
# def get_notified(sender, **kwargs):
#     """ Printing a notification string. """
#     print("HTTP request finished")
