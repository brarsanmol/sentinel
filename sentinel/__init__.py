from sentinel.main import Sentinel

sentinel = Sentinel()
sentinel.run(sentinel.configuration.get("Discord", "Token"))

__version__ = "0.1.0"
