import unittest
import subprocess
import os
import copy


class RHQueueTests(unittest.TestCase):
  v = "/homes/pmcd/venv/test-slurm"
  t = "1"
  o = "my.stdout"
  p = "3"
  e = "peter.nicolas.castenschiold.mcdaniel@regionh.dk"
  b = 3
  args_lst = []
  base_args = ["v", "t", "o"]
  begin_args = ["v", "t", "o", "p"]

  def args(self, file, args=["v", "t", "o"]):

    ret = ["rhqueue", file]
    for val in args:
      ret.extend([f"-{val}", getattr(self, val)])
    return ret

  def test_create_file(self):
    script = subprocess.run(self.args("test_create_file.py"))
    self.assertEqual(script.returncode, 0)
    self.assertTrue(os.path.isfile("./new_file.txt"))

  def test_tensorflow(self):
    script = subprocess.run(self.args("test_tensorflow.py"))
    self.assertEqual(script.returncode, 0)

  def test_without_venv(self):
    val = copy.copy(self.base_args)
    val.remove("v")
    script = subprocess.run(self.args("test_venv.py", val))
    self.assertEqual(script.returncode, 0)

  def test_with_venv(self):
    script = subprocess.run(self.args("test_venv.py"))
    self.assertEqual(script.returncode, 0)

  def test_with_envvar_venv(self):
    val = copy.copy(self.base_args)
    val.remove("v")
    subprocess.run(f"export RHQ_VENV=\"{self.v}\"", shell=True)
    script = subprocess.run(self.args("test_venv.py", val))
    self.assertEqual(script.returncode, 0)

  def test_begin_time(self):
    self.begin_time = "1"
    script = subprocess.run(self.args("test_venv.py", self.base_args))

  def test_output_file(self):
    self.o = "test.stdout"
    script = subprocess.run(self.args("test_venv.py"))
    self.assertEqual(script.returncode, 0)
    self.assertTrue(os.path.isfile(self.o))


if __name__ == "__main__":
  test = RHQueueTests()
  print(test.args(""))
  unittest.main()