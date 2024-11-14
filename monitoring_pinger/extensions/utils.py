# Service module to support extensions
from contextlib import suppress
from . import store
def when_service_is_up(service_name):
    def _wrapper(func):
        
        def validate_status(response):
            print(service_name)
            if response['services'].get(service_name, '') != 'Operational':
                return
            with suppress():
                return func(response)
            
        return validate_status
    return _wrapper


def extension(func):
    """
    Decorator to enrich a response with custom data.

    usage:
    @extension
    def some_func(response):
        # fooing & baring the response
        return response
    """
    store.extensions.append(func)

    def _wrapper(response):
        print(response.get(func.__name__, ''))
        with suppress():
            return func(response)
    
    return _wrapper