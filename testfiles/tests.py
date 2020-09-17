from argparse import Namespace
from sys import argv
import unittest
import subprocess
import os
import copy
import inspect
import time
import glob
from pathlib import Path
from rhqueue.parser import RHQueueParser


class RHQueueTests(unittest.TestCase):
  v = "/homes/pmcd/venv/test-slurm"
  s = "1"
  o = "my.stdout"
  p = "3"
  e = "peter.nicolas.castenschiold.mcdaniel@regionh.dk"
  b = "3"
  args_lst = []
  base_args = ["v", "s", "o"]
  begin_args = ["v", "s", "o", "p"]

  def args(self, file, args=["v", "s", "o"]):

    ret = ["rhqueue", "queue", file]
    for val in args:
      ret.extend([f"-{val}", getattr(self, val)])
    return ret

  def assertFileContentsSame(self, file, expected):
    val = ""
    counter = 0
    time.sleep(3)
    if os.path.isfile(file):
      with open(file, "r") as f:
        val = f.read().rstrip("\n")
    else:
      raise Exception(f"file {file} is hanging indefinitly")
    self.assertEqual(val, expected)

  def test_create_file(self):
    self.o = f"{inspect.currentframe().f_code.co_name}.stdout"
    script = subprocess.run(self.args("test_create_file.py"))
    self.assertEqual(script.returncode, 0)
    time.sleep(2)
    self.assertTrue(os.path.isfile("./new_file.txt"))
    self.assertFileContentsSame("./new_file.txt", "new file is created")

  def test_without_venv(self):
    val = copy.copy(self.base_args)
    val.remove("v")
    self.o = f"{inspect.currentframe().f_code.co_name}.stdout"
    script = subprocess.run(self.args("test_venv.py", val))
    self.assertEqual(script.returncode, 0)
    self.assertFileContentsSame(self.o, "None")

  def test_with_venv(self):
    self.o = f"{inspect.currentframe().f_code.co_name}.stdout"
    script = subprocess.run(self.args("test_venv.py"))
    self.assertEqual(script.returncode, 0)
    self.assertFileContentsSame(self.o, self.v)

  def test_with_envvar_venv(self):
    self.o = f"{inspect.currentframe().f_code.co_name}.stdout"
    val = copy.copy(self.base_args)
    val.remove("v")
    os.environ["RHQ_VENV"] = self.v
    script = subprocess.run(self.args("test_venv.py", val))
    self.assertEqual(script.returncode, 0)
    del os.environ["RHQ_VENV"]
    self.assertFileContentsSame(self.o, self.v)

  def test_begin_time(self):
    self.b = "1"
    script = subprocess.run(self.args("test_venv.py", self.base_args + ["b"]))
    self.assertEqual(script.returncode, 0)

  def test_output_file(self):
    self.o = "test_output_file.stdout"
    script = subprocess.run(self.args("test_venv.py"))
    self.assertEqual(script.returncode, 0)
    self.assertFileContentsSame(self.o, "/homes/pmcd/venv/test-slurm")

  def test_shebang_env(self):
    self.o = "test_shebang_env.stdout"
    script = subprocess.run(self.args("test_shebang_env.py"))
    self.assertEqual(script.returncode, 0)
    self.assertFileContentsSame(self.o,
                                "/homes/pmcd/venv/test-slurm/bin/python")

  def test_shebang_venv(self):
    self.o = "test_shebang_venv.stdout"
    script = subprocess.run(self.args("test_shebang_venv.py"))
    self.assertEqual(script.returncode, 0)
    self.assertFileContentsSame(self.o,
                                "/homes/pmcd/venv/test-slurm/bin/python3")

  def test_shebang_bin(self):
    self.o = "test_shebang_bin.stdout"
    script = subprocess.run(self.args("test_shebang_bin.py"))
    self.assertEqual(script.returncode, 0)
    self.assertFileContentsSame(self.o, "/usr/bin/python3")

  def test_multiple_titans(self):
    self.o = "test_multiple_titans.stdout"
    for i in [1, 2, 3, 4, 5, 7]:
      with self.subTest(titan=f"titan{i}"):
        self._sub_titan_test(titan=f"titan{i}")

  def _sub_titan_test(self, titan):
    self.o = f"test_multiple_{titan}.stdout"
    self.s = titan
    script = subprocess.run(self.args("test_titan_hostname.py"))
    self.assertEqual(script.returncode, 0)
    self.assertFileContentsSame(self.o, titan)


if __name__ == "__main__":
  unittest.main()
