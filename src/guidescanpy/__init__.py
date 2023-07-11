from importlib.resources import read_text
import logging
import guidescanpy
from guidescanpy.config import Config

try:
    from guidescanpy._version import version as __version__  # type: ignore
except ModuleNotFoundError:
    # We're likely running as a source package without installation
    __version__ = "src"


config = Config(read_text(guidescanpy, "config.json"))
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
