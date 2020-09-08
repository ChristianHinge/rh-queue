import argparse
from argparse import Namespace
from typing import Any

class ScriptNameAction(argparse.Action):
  def __init__(self, option_strings, dest, nargs=None, **kwargs) -> None:
    if nargs is not None:
      raise ValueError("nargs is not allowed")
    super(ScriptNameAction, self).__init__(option_strings, dest, **kwargs)
  def __call__(self, parser, namespace, values, option_strings, **kwargs) -> Any:
      setattr(namespace, self.dest, values) 