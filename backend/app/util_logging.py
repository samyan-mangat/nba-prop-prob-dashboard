import logging
import sys

LEVEL = logging.INFO

root = logging.getLogger()
if not root.handlers:
    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)
root.setLevel(LEVEL)

get_logger = logging.getLogger