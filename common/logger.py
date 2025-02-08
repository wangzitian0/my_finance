# common/logger.py
import os
import logging
from datetime import datetime
from .config import load_common_config
from .snowflake import Snowflake


class LogIDFilter(logging.Filter):
    def __init__(self, logid):
        super().__init__()
        self.logid = logid

    def filter(self, record):
        record.logid = self.logid
        return True


def setup_logger(job_id, date_str=None):
    """
    Set up a logger using configuration from common_config.yml.
    Logs are written to data/log/<job_id>/<date_str>.txt.
    All log messages (including errors with stack traces) are written to the file only.
    A unique logid (generated using a Snowflake algorithm) is attached to each log record.
    """
    config = load_common_config()
    log_conf = config.get("logging", {})
    log_level = getattr(logging, log_conf.get("level", "INFO"))
    file_level = getattr(logging, log_conf.get("file_level", "INFO"))
    # Default format includes the logid. You can override it in common_config.yml.
    log_format = log_conf.get("format", '%(asctime)s - %(levelname)s - [%(logid)s] - %(message)s')

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

    # Disable propagation so that messages do not bubble up to the root logger.
    logger.propagate = False

    formatter = logging.Formatter(log_format)

    # File handler for detailed logs (all messages go to the file)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(file_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Generate a unique logid using the Snowflake algorithm and attach it via a filter.
    sf = Snowflake(machine_id=1)
    logid = sf.get_id()
    logger.addFilter(LogIDFilter(logid))

    return logger
