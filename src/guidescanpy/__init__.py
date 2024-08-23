from importlib.resources import files
import logging
import guidescanpy
from guidescanpy.configuration import Config

try:
    from guidescanpy._version import version as __version__  # type: ignore
except ModuleNotFoundError:
    # We're likely running as a source package without installation
    __version__ = "src"


config = Config(files(guidescanpy) / "config.yaml")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
