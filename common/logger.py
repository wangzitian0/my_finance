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
    模拟的文件流对象，将写入内容重定向到日志记录器中。
    用于捕获底层库（例如第三方库）的 stderr 输出，并将其写入日志。
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
    根据 common/common_config.yml 中的配置初始化日志记录器。
    日志写入路径为：data/log/<job_id>/<date_str>.txt
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

    # 构建日志文件路径：data/log/<job_id>/<date_str>.txt
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
    # 禁用传播，防止消息输出到 root logger
    logger.propagate = False
    formatter = logging.Formatter(log_format)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(file_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addFilter(DefaultRequestLogIDFilter())
    return logger
