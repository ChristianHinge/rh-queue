import argparse
import os



class FooAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(FooAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class ScriptTypeHandler:
    def __init__(self) -> None:
        pass

    def python(self, fname):
        return os.path.abspath(fname)

    def shell(self, fname):
        return fname

    def bash(self, fname):
        return f"bash {os.path.abspath(fname)}"

    def text(self, fname):
        return f"cat {fname}"

    def any(self, fname):
        return fname


class ScriptTypeAction(argparse.Action):
    handler = ScriptTypeHandler()
    matches = {
        "*.txt": handler.text,
        "*.py": handler.python,
        "*.sh": handler.bash,
    }

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ScriptTypeAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        call_value = self.find_match(values)
        setattr(namespace, self.metavar, values)
        setattr(namespace, "full_script", call_value)

    def find_match(self, fname):
        from fnmatch import fnmatch
        for k, v in self.matches.items():
            if fnmatch(fname, k):
                return v(fname)
        return self.handler.any(fname)


def priority_action(values):
    class PriorityDefaultAction(argparse.Action):
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            self.default_values = values
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super(ScriptTypeAction, self).__init__(option_strings, dest, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            if values:
                setattr(namespace, self.metavar, values)
            for i in self.default_values:
                if i:
                    setattr(namespace, self.metavar, i)
                    break
    return PriorityDefaultAction