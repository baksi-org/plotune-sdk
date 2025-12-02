from diskcache import Cache
from platformdirs import user_cache_dir


APP_NAME = "Plotune"
APP_AUTHOR = "BAKSI"
USER_CACHE_DIR = user_cache_dir(APP_NAME, APP_AUTHOR)