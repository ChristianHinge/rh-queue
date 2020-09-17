from rhqueue import RHQueueParser, get_open_servers
import unittest
import os


class RHQueueParserTester(unittest.TestCase):
  def list_to_args_string(self, lst):
    if isinstance(lst, list):
      return " ".join(lst)
    return lst

  def setUp(self):
    self.open_titans = get_open_servers("titan[1-7]")

  def get_args(self, script="test_venv.py", **kwargs):
    args = ["queue"]
    for i in kwargs.items():
      if len(i[0]) == 1:
        args.append(f"-{i[0]}")
        args.append(f"{self.list_to_args_string(i[1])}")
      else:
        args.append(f"--{i[0].replace('_', '-')}")
        args.append(f"{self.list_to_args_string(i[1])}")
    args.append(script)
    return RHQueueParser(argv=args).args

  def test_specific_titan(self):
    self.t = "titan1"
    res = self.get_args(s=self.t)
    self.assertEqual(["titan1"], res.servers.as_list())

  def test_titan_list(self):
    titan = "titan[1,2]"
    res = self.get_args(s=titan)
    self.assertEqual(["titan1", "titan2"], res.servers.as_list())

  def test_titan_list_seperate(self):
    titan = "titan[1,3]"
    res = self.get_args(s=titan)
    self.assertEqual(["titan1", "titan3"], res.servers.as_list())

  def test_titan_range(self):
    titans = "titan[1-3]"
    res = self.get_args(s=titans)
    self.assertEqual(["titan1", "titan2", "titan3"], res.servers.as_list())

  def test_titan_multiple_with_range(self):
    titans = "titan[1-3,4]"
    res = RHQueueParser(argv=["queue", "-s", titans, "./test_venv.py"]).args
    self.assertEqual(["titan1", "titan2", "titan3", "titan4"],
                     res.servers.as_list())

  def test_titan_exclude_list(self):
    open_titans = set(map(lambda x: f"titan{x}", range(1, 8)))
    titans = "titan[1-3]"
    res = self.get_args(s=titans)
    self.assertEqual(res.servers.invert.as_list(),
                     ["titan4", "titan5", "titan6", "titan7"])

  def test_script_name(self):
    script_name = "test1"
    res = RHQueueParser(
        argv=["queue", "--script-name", script_name, "./test_venv.py"]).args
    self.assertEqual(script_name, res.script_name)

  def test_venv_base(self):
    res = self.get_args()
    self.assertEqual("test_venv.py", res.script_name)

  def test_venv_environ(self):
    os.environ["RHQ_VENV"] = "/homes/pmcd/venv/test-slurm"
    res = self.get_args()
    self.assertEqual("/homes/pmcd/venv/test-slurm", res.venv)

  def test_venv_virtual_env(self):
    os.environ["VIRTUAL_ENV"] = "/homes/pmcd/venv/test-slurm"
    res = self.get_args()
    self.assertEqual(os.environ["VIRTUAL_ENV"], res.venv)

  def test_venv_priority_environ(self):
    os.environ["RHQ_VENV"] = "/homes/pmcd/venv/test-slurm"
    venv = "/homes/pmcd/venv/django-venv"
    res = self.get_args(venv=venv)
    self.assertEqual(venv, res.venv)

  def test_venv_priority_virtual_env(self):
    os.environ["VIRTUAL_ENV"] = "/homes/pmcd/venv/test-slurm"
    venv = "/homes/pmcd/venv/django-venv"
    res = self.get_args(venv=venv)
    self.assertEqual(venv, res.venv)

  def test_venv_priority_virtual_env_environ(self):
    os.environ["RHQ_VENV"] = "RHQ"
    os.environ["VIRTUAL_ENV"] = "VIR_ENV"
    res = self.get_args()
    self.assertEqual(os.environ["VIRTUAL_ENV"], res.venv)

  def test_venv_priority_all(self):
    os.environ["RHQ_VENV"] = "RHQ"
    os.environ["VIRTUAL_ENV"] = "VIR_ENV"
    venv = "VENV"
    res = self.get_args(venv=venv)
    self.assertEqual(venv, res.venv)


if __name__ == "__main__":
  unittest.main()