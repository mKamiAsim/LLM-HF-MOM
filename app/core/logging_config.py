import seqlog
import logging
import os


SEQ_URL = os.getenv("SEQ_SERVER_URL", "http://localhost:5341")
SEQ_API_KEY = os.getenv("SEQ_API_KEY")
# seqlog.log_to_seq(
#    server_url=SEQ_URL,
#    api_key="5Z8II2S4PEgYWehtEuEG",
#    level=logging.INFO,
#    batch_size=10,
#    auto_flush_timeout=10,  # seconds
#    override_root_logger=True,
#    json_encoder_class=None,  # Optional; only specify this if you want to use a custom JSON encoder
#    support_extra_properties=True # Optional; only specify this if you want to pass additional log record properties via the "extra" argument.
# )

seqlog.configure_from_dict({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        }
    },
    "handlers": {
        "seq": {
            "class": "seqlog.structured_logging.SeqLogHandler",
            "server_url": SEQ_URL,  # replace with your Seq URL
            "api_key": SEQ_API_KEY,
            "formatter": "default",
            "batch_size": 1,  # Important for real-time
            "auto_flush_timeout": 1  # Seconds, lower is better for real-time
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "seq"]
    },
})


logger = logging.getLogger(__name__)

# logger = logging.getLogger(__name__)
# stream_handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# stream_handler.setFormatter(formatter)
# logger.addHandler(stream_handler)