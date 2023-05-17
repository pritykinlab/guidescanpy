from importlib.resources import read_text
import guidescanpy
from guidescanpy.config import Config

try:
    from guidescanpy._version import version as __version__  # type: ignore
except ModuleNotFoundError:
    # We're likely running as a source package without installation
    __version__ = "src"


config = Config(read_text(guidescanpy, "config.json"))
