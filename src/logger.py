import logging
import os
from datetime import datetime


def get_logger(name):
    """Return a logger with the specified name."""

    # Logging hierarchy below:
    # logs/
    #   2024/
    #     January/
    #       2024-01-01.log
    #       2024-01-02.log
    #       ...
    #     February/
    #       ...
    #   2025/
    #     ...

    current_date = datetime.now()
    LOG_PATH = os.path.join(
        "logs",
        os.path.join(
            str(current_date.year),
            str(current_date.strftime("%B")),
        ),
    )
    os.makedirs(LOG_PATH, exist_ok=True)

    logger = logging.getLogger(name)
    logging.basicConfig(
        filename=os.path.join(LOG_PATH, f"{current_date.strftime("%Y-%m-%d")}.log"),
        encoding="utf-8",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    return logger
