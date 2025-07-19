def register_generator_method(method_name=None):
    """
    Decorator to register a function as a method of the given class.
    Usage:
        @register_generator_method(VideoProjectGenerator, 'generate_openshot_project')
        def generate_openshot_project(self, ...):
            ...
    """
    def decorator(func):
        name = method_name or func.__name__
        setattr(name, func)
        return func
    return decorator
