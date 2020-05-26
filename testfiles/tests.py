import unittest
import subprocess
import os
import copy
import inspect
import time
import glob


class RHQueueTests(unittest.TestCase):
  v = "/homes/pmcd/venv/test-slurm"
  t = "1"
  o = "my.stdout"
  p = "3"
  e = "peter.nicolas.castenschiold.mcdaniel@regionh.dk"
  b = "3"
  args_lst = []
  base_args = ["v", "t", "o"]
  begin_args = ["v", "t", "o", "p"]

  def args(self, file, args=["v", "t", "o"]):

    ret = ["rhqueue", file]
    for val in args:
      ret.extend([f"-{val}", getattr(self, val)])
    return ret

  def assertFileContentsSame(self, file, expected):
    val = ""
    while not os.path.isfile(file):
      with open(self.o, "r") as f:
        val = f.read().rstrip("\n")
    self.assertEqual(val, expected)

  def test_create_file(self):
    self.o = f"{inspect.currentframe().f_code.co_name}.stdout"
    script = subprocess.run(self.args("test_create_file.py"))
    self.assertEqual(script.returncode, 0)
    self.assertTrue(os.path.isfile("./new_file.txt"))
    self.assertFileContentsSame("./new_file.txt", "new file is created")

  def test_tensorflow(self):
    self.o = f"{inspect.currentframe().f_code.co_name}.stdout"
    script = subprocess.run(self.args("test_tensorflow.py"))
    self.assertEqual(script.returncode, 0)

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
    self.o = f"{inspect.currentframe().f_code.co_name}.stdout"
    self.b = "1"
    script = subprocess.run(self.args("test_venv.py", self.base_args + ["b"]))
    self.assertEqual(script.returncode, 0)
    self.assertFileContentsSame(self.o, self.v)

  def test_output_file(self):
    self.o = "test_output_file.stdout"
    script = subprocess.run(self.args("test_venv.py"))
    self.assertEqual(script.returncode, 0)
    self.assertTrue(os.path.isfile(self.o))

  @classmethod
  def tearDownClass(cls):
    files = glob.glob("*.stdout")
    files += glob.glob("*.txt")
    for file in files:
      os.remove(f"./{file}")
if __name__ == "__main__":
  test = RHQueueTests()
  print(test.args(""))
  unittest.main()