import os
import logging
from datetime import datetime
from .config import load_common_config
from .snowflake import Snowflake


class DefaultRequestLogIDFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'request_logid'):
            record.request_logid = "N/A"
        return True


def setup_logger(job_id, date_str=None):
    """
    Set up a logger using configuration from common_config.yml.
    Logs are written to data/log/<job_id>/<date_str>.txt.
    A unique logid is added for each request via a LoggerAdapter.
    Additionally, every log record gets a default 'request_logid' (if not provided)
    so that the log format does not cause an error.
    """
    config = load_common_config()
    log_conf = config.get("logging", {})
    log_level = getattr(logging, log_conf.get("level", "INFO"))
    file_level = getattr(logging, log_conf.get("file_level", "INFO"))
    # The log format should include %(request_logid)s:
    log_format = log_conf.get("format", '%(asctime)s - %(levelname)s - [%(request_logid)s] - %(message)s')

    if date_str is None:
        date_str = datetime.now().strftime("%y%m%d-%H%M%S")

    # Construct log file path: data/log/<job_id>/<date_str>.txt
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    log_base_dir = os.path.join(root_dir, "data", "log")
    log_dir = os.path.join(log_base_dir, job_id)
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{date_str}.txt")

    logger_name = f"{job_id}_{date_str}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Disable propagation so messages don't go to the root logger
    logger.propagate = False

    formatter = logging.Formatter(log_format)

    # File handler for detailed logs (all messages go to file)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(file_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Add the default filter so every record gets a request_logid
    logger.addFilter(DefaultRequestLogIDFilter())

    return logger
