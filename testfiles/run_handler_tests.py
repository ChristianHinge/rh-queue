import unittest
import subprocess
import os
import inspect
import time


class RHQueueTests(unittest.TestCase):
    v = "/homes/pmcd/venv/test-slurm"
    s = "1"
    o = "my.stdout"
    p = "3"
    e = "peter.nicolas.castenschiold.mcdaniel@regionh.dk"
    args_lst = []
    base_args = ["v", "s", "o"]

    def list_to_args_string(self, lst):
        if isinstance(lst, list):
            return " ".join(lst)
        return lst

    def args(self, script, *arg_vals, **kwargs):

        ret = ["rhqueue", "queue", script]
        for key, val in kwargs.items():
            if len(key) == 1:
                ret.append(f"-{key}")
                ret.append(f"{self.list_to_args_string(val)}")
            else:
                ret.append(f"--{key.replace('_', '-')}")
                ret.append(f"{self.list_to_args_string(val)}")
        ret.extend(arg_vals)
        return ret

    def assertFileContentsSame(self, file, expected):
        val = ""
        time.sleep(3)
        if os.path.isfile(file):
            while os.path.getsize(file) == 0:
                time.sleep(1)
            with open(file, "r") as f:
                val = f.read().rstrip("\n")
        else:
            raise Exception(f"file {file} is hanging indefinitly")
        self.assertEqual(val, expected)

    def test_create_file(self):
        output_file = f"{inspect.currentframe().f_code.co_name}.stdout"
        script = subprocess.run(
            self.args("test_create_file.py", o=output_file, e=self.e))
        self.assertEqual(script.returncode, 0)
        time.sleep(2)
        self.assertTrue(os.path.isfile("./new_file.txt"))
        self.assertFileContentsSame("./new_file.txt", "new file is created")

    def test_without_venv(self):
        output_file = f"{inspect.currentframe().f_code.co_name}.stdout"
        script = subprocess.run(
            self.args("test_venv.py", o=output_file, v=self.v, e=self.e))
        self.assertEqual(script.returncode, 0)
        self.assertFileContentsSame(output_file, "/homes/pmcd/venv/test-slurm")

    def test_with_venv(self):
        output_file = f"{inspect.currentframe().f_code.co_name}.stdout"
        script = subprocess.run(
            self.args("test_venv.py", o=output_file, v=self.v, e=self.e))
        self.assertEqual(script.returncode, 0)
        self.assertFileContentsSame(output_file, "/homes/pmcd/venv/test-slurm")

    def test_with_envvar_venv(self):
        v = "/homes/pmcd/venv/test-slurm"
        os.environ["RHQ_ENV"] = v
        output_file = f"{inspect.currentframe().f_code.co_name}.stdout"
        script = subprocess.run(
            self.args("test_venv.py", o=output_file, v=v, e=self.e))
        self.assertEqual(script.returncode, 0)
        del os.environ["RHQ_ENV"]
        self.assertFileContentsSame(output_file, v)

    def test_begin_time(self):
        output_file = f"{inspect.currentframe().f_code.co_name}.stdout"
        script = subprocess.run(
            self.args("test_venv.py", b="1", o=output_file, v=self.v,
                      e=self.e))
        self.assertEqual(script.returncode, 0)

    def test_output_file(self):
        output_file = f"{inspect.currentframe().f_code.co_name}.stdout"
        script = subprocess.run(
            self.args("test_venv.py", o=output_file, v=self.v, e=self.e))
        self.assertEqual(script.returncode, 0)
        self.assertFileContentsSame(output_file, "/homes/pmcd/venv/test-slurm")

    def test_shebang_env(self):
        output_file = f"{inspect.currentframe().f_code.co_name}.stdout"
        script = subprocess.run(
            self.args("test_shebang_env.py", o=output_file, v=self.v,
                      e=self.e))
        self.assertEqual(script.returncode, 0)
        time.sleep(2)
        self.assertFileContentsSame(output_file,
                                    "/homes/pmcd/venv/test-slurm/bin/python")

    def test_shebang_venv(self):
        output_file = f"{inspect.currentframe().f_code.co_name}.stdout"
        script = subprocess.run(
            self.args("test_shebang_venv.py",
                      o=f"{inspect.currentframe().f_code.co_name}.stdout",
                      v=self.v))
        self.assertEqual(script.returncode, 0)
        self.assertFileContentsSame(output_file,
                                    "/homes/pmcd/venv/test-slurm/bin/python3")

    def test_shebang_bin(self):
        output_file = f"{inspect.currentframe().f_code.co_name}.stdout"
        script = subprocess.run(
            self.args("test_shebang_bin.py", o=output_file, v=self.v))
        self.assertEqual(script.returncode, 0)
        self.assertFileContentsSame(output_file, "/usr/bin/python3")

    def test_tensorflow(self):
        ouptut_file = f"test_tensorflow.stdout"
        script = subprocess.run(
            self.args("./test_tensorflow.py", o=ouptut_file, c="test-tf"))
        self.assertEqual(script.returncode, 0)

    def test_source_script(self):
        source_script = "base.sh"
        output_file = f"{inspect.currentframe().f_code.co_name}.stdout"
        script = subprocess.run(
            self.args("./test_source_script.py",
                      source_script=source_script,
                      o=output_file))
        self.assertEqual(script.returncode, 0)
        self.assertFileContentsSame(output_file, "test")

    def test_email(self):
        email = "peter.nicolas.castenschiold.mcdaniel@regionh.dk"
        script = subprocess.run(self.args("./test_venv.py", v=self.v, e=email))
        self.assertEqual(script.returncode, 0)

    def test_email_env(self):
        os.environ[
            "RHQ_EMAIL"] = "peter.nicolas.castenschiold.mcdaniel@regionh.dk"
        script = subprocess.run(self.args("./test_timeout.py"))
        self.assertEqual(script.returncode, 0)


if __name__ == "__main__":
    unittest.main()
