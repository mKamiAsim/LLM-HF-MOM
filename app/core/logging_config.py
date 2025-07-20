import seqlog
import logging
import os


SEQ_URL = os.getenv("SEQ_SERVER_URL", "http://localhost:5341")

seqlog.log_to_seq(
   server_url=SEQ_URL,
   api_key="5Z8II2S4PEgYWehtEuEG",
   level=logging.INFO,
   batch_size=10,
   auto_flush_timeout=10,  # seconds
   override_root_logger=True,
   json_encoder_class=None,  # Optional; only specify this if you want to use a custom JSON encoder
   support_extra_properties=True # Optional; only specify this if you want to pass additional log record properties via the "extra" argument.
)

logger = logging.getLogger(__name__)

# logger = logging.getLogger(__name__)
# stream_handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# stream_handler.setFormatter(formatter)
# logger.addHandler(stream_handler)