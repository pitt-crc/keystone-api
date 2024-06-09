from django.conf import settings

NOTIFY_ALLOC_THRESHOLDS = getattr(settings, "NOTIFY_ALLOC_THRESHOLDS", [90])
NOTIFY_STATUS_UPDATE = getattr(settings, "NOTIFY_STATUS_UPDATE", True)
NOTIFY_EXPIRY_THRESHOLDS = getattr(settings, "NOTIFY_EXPIRY_THRESHOLDS", [10])
