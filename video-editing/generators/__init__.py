import importlib
import pkgutil

def _register_generators(cls):
    import generators
    for _, modname, _ in pkgutil.iter_modules(generators.__path__):
        if modname.startswith("generators_"):
            mod = importlib.import_module(f"generators.{modname}")
            for name in dir(mod):
                if name.startswith("generate_"):
                    func = getattr(mod, name)
                    if callable(func):
                        setattr(cls, name, func)
