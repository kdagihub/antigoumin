import logging

from geniuspay import signals as gp_signals
from django.dispatch import receiver

from .services import apply_geniuspay_event

logger = logging.getLogger(__name__)


@receiver(gp_signals.payment_success)
def on_geniuspay_success(sender, transaction=None, raw_event=None, **kwargs):
    apply_geniuspay_event(raw_event, transaction)


@receiver(gp_signals.payment_failed)
@receiver(gp_signals.payment_cancelled)
@receiver(gp_signals.payment_expired)
def on_geniuspay_failed(sender, transaction=None, raw_event=None, **kwargs):
    apply_geniuspay_event(raw_event, transaction)


@receiver(gp_signals.payment_refunded)
def on_geniuspay_refunded(sender, transaction=None, raw_event=None, **kwargs):
    logger.info("Remboursement GeniusPay reçu : %s", getattr(transaction, "reference", None))
    apply_geniuspay_event(raw_event, transaction)
