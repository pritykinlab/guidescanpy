try:
    from guidescan._version import version as __version__  # type: ignore
except ModuleNotFoundError:
    # We're likely running as a source package without installation
    __version__ = 'src'
