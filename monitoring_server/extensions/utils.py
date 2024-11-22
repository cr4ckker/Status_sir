# Service module to support extensions
from contextlib import suppress
from . import store

def _process_extensions(event):
    for _extension in store.extensions:
        _extension(event)

def extension(func):
    """
    Decorator to add an extension to server

    usage:
    @extension
    def some_func(event_data):
        # some extension code

    """
    store.extensions.append(func)

    def _wrapper(response):
        print(response.get(func.__name__, ''))
        with suppress():
            return func(response)
    
    return _wrapper