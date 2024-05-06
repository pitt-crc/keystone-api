import logging

# Disable health check logging
# Avoids spamming the console with health check messages
logging.getLogger('health-check').setLevel(1000)
