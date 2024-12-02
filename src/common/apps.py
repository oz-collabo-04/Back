from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"

    def ready(self):
        import common.signals.chat_signals
        import common.signals.estimation_signals
        import common.signals.notification_signals
        import common.signals.request_signals
        import common.signals.reservation_signals
        import common.signals.review_signals
