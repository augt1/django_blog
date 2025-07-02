from .base import *


INSTALLED_APPS += [
    'debug_toolbar',

]

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE


# Debug Toolbar settings
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]