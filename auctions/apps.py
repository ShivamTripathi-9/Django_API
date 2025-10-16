# auctions/apps.py
from django.apps import AppConfig
import threading
import time
import logging

logger = logging.getLogger(__name__)

class AuctionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auctions'

    def ready(self):
        # Start background thread to monitor auctions. Be careful to not start multiple threads in dev reload.
        if not hasattr(self, 'thread_started'):
            from django.conf import settings
            import os
            # Avoid starting thread during manage.py commands like makemigrations in some cases:
            if os.environ.get('RUN_MAIN') != 'true' and os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
                # If using runserver, Django may spawn two processes; we want to run only in main.
                # However for simplicity in dev, we start anyway if RUN_MAIN is true.
                pass

            t = threading.Thread(target=self._monitor_auctions, daemon=True)
            t.start()
            self.thread_started = True

    def _monitor_auctions(self):
        from django.utils import timezone
        from .models import Auction
        from .tasks import close_auction
        poll_interval = 5  # seconds
        logger.info("Starting auction monitor thread (polling every %s seconds)", poll_interval)
        while True:
            try:
                now = timezone.now()
                # fetch auctions that are not closed and whose end_time <= now
                auctions_to_close = Auction.objects.filter(end_time__lte=now).exclude(status='closed')
                for a in auctions_to_close:
                    try:
                        result = close_auction(a.id)
                        logger.info("Closed auction %s: %s", a.id, result)
                    except Exception as e:
                        logger.exception("Error closing auction %s: %s", a.id, e)
            except Exception as exc:
                logger.exception("Auction monitor exception: %s", exc)
            time.sleep(poll_interval)
