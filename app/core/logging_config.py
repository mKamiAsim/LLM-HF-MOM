import seqlog
import logging
import os


SEQ_URL = os.getenv("SEQ_SERVER_URL", "http://localhost:5341")
SEQ_API_KEY = os.getenv("SEQ_API_KEY")
# seqlog.log_to_seq(
#    server_url=SEQ_URL,
#    api_key=SEQ_API_KEY,
#    level=logging.INFO,
#    batch_size=10,
#    auto_flush_timeout=10,  # seconds
#    override_root_logger=True,
#    json_encoder_class=None,  # Optional; only specify this if you want to use a custom JSON encoder
#    support_extra_properties=True # Optional; only specify this if you want to pass additional log record properties via the "extra" argument.
# )


# logger = logging.getLogger(__name__)

# # logger = logging.getLogger(__name__)
# # stream_handler = logging.StreamHandler()
# # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# # stream_handler.setFormatter(formatter)
# # logger.addHandler(stream_handler)

def setup_logging():
    seqlog.configure_from_file("log_config.yml")
    
#    seqlog.configure_from_dict({
#     "version": 1,
#     "disable_existing_loggers": True,
#     "root": {
#         "level": "INFO",
#         "handlers": [
#             "seq",
#             "console"
#         ]
#     },
#     "loggers": {
#         "another_logger": {
#             "propagate": False,
#             "level": "INFO",
#             "handlers": [
#                 "seq",
#                 "console"
#             ]
#         }
#     },
#     "handlers": {
#         "console": {
#             "class": "seqlog.structured_logging.ConsoleStructuredLogHandler",
#             "formatter": "seq"
#         },
#         "seq": {
#             "class": "seqlog.structured_logging.SeqLogHandler",
#             "formatter": "seq",
#             "server_url": SEQ_URL,
#             "api_key": SEQ_API_KEY,
#             "json_encoder_class": "json.encoder.JSONEncoder"
#         }
#     },
#     "formatters": {
#         "seq": {
#             "style": "{"
#         }
#     }
# })