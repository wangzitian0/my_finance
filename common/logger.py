# common/logger.py
import logging
import os
from datetime import datetime

from .config import load_common_config
from .snowflake import Snowflake


class DefaultRequestLogIDFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "request_logid"):
            record.request_logid = "N/A"
        return True


class StreamToLogger(object):
    """
    Mock file stream object that redirects write content to logger.
    Used to capture stderr output from underlying libraries (e.g., third-party libraries) and write to log.
    """

    def __init__(self, logger, log_level=logging.ERROR):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def setup_logger(job_id, date_str=None):
    """
    Initialize logger based on configuration in common/common_config.yml.
    Log write path: data/log/<job_id>/<date_str>.txt
    """
    config = load_common_config()
    log_conf = config.get("logging", {})
    log_level = getattr(logging, log_conf.get("level", "INFO"))
    file_level = getattr(logging, log_conf.get("file_level", "INFO"))
    log_format = log_conf.get(
        "format", "%(asctime)s - %(levelname)s - [%(request_logid)s] - %(message)s"
    )

    if date_str is None:
        date_str = datetime.now().strftime("%y%m%d-%H%M%S")

    # Build log file path: data/log/<job_id>/<date_str>.txt
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
    # Disable propagation to prevent messages from outputting to root logger
    logger.propagate = False
    formatter = logging.Formatter(log_format)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(file_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addFilter(DefaultRequestLogIDFilter())
    return logger
