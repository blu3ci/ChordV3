# flake8: noqa

import logging
import sys
import traceback

from colorama import Fore, Style, init

init(autoreset=True)


class ChordFormatter(logging.Formatter):
    DATE = f"{Fore.BLUE}%(asctime)s{Fore.RESET}"
    NAME = f"{Fore.MAGENTA}%(name)s{Fore.RESET}"
    LEVEL_NAME = "%(levelname)s"
    MESSAGE = f"{Fore.GREEN}%(message)s{Fore.RESET}"
    GREY_DASH = f"{Fore.BLACK}-{Fore.RESET}"

    FORMATS = {
        logging.DEBUG: f"{DATE} {GREY_DASH} {NAME} {GREY_DASH} {LEVEL_NAME} {GREY_DASH} {MESSAGE}",
        logging.INFO: f"{DATE} {GREY_DASH} {NAME} {GREY_DASH} {Fore.LIGHTGREEN_EX}{LEVEL_NAME} {GREY_DASH} {MESSAGE}",
        logging.WARNING: f"{DATE} {GREY_DASH} {NAME} {GREY_DASH} {Fore.YELLOW}{LEVEL_NAME} {GREY_DASH} {MESSAGE}",
        logging.ERROR: f"{DATE} {GREY_DASH} {NAME} {GREY_DASH} {Fore.RED}{LEVEL_NAME} {GREY_DASH} {MESSAGE}",
        logging.CRITICAL: f"{DATE} {GREY_DASH} {NAME} {GREY_DASH} {Style.BRIGHT}{Fore.RED}{LEVEL_NAME} {GREY_DASH} {MESSAGE}",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    def exception_handler(type, value, tb):
        if issubclass(type, KeyboardInterrupt):
            sys.__excepthook__(type, value, tb)
            return

        logger.error("\n".join(traceback.format_exception(type, value, tb)))

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(ChordFormatter())

    logger.addHandler(stream_handler)

    sys.excepthook = exception_handler

    return logger
