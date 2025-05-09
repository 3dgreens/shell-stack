import logging

from textual.logging import TextualHandler


def get_logger(name: str | None = None, log_level: int = logging.DEBUG) -> logging.Logger:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            # TODO: Maybe consider other handlers and make sure
            #       we can log to file
            TextualHandler()
        ],
    )
    return logging.getLogger(name)
