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

  def get_args(self, cmd="queue", script="test_venv.py", **kwargs):
    args = [cmd]
    args.append(script)
    for i in kwargs.items():
      if len(i[0]) == 1:
        args.append(f"-{i[0]}")
        args.append(f"{self.list_to_args_string(i[1])}")
      else:
        args.append(f"--{i[0].replace('_', '-')}")
        args.append(f"{self.list_to_args_string(i[1])}")
    # print(" ".join(args))
    return RHQueueParser(argv=" ".join(args)).args

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
    res = self.get_args(s=titans)
    self.assertEqual(["titan1", "titan2", "titan3", "titan4"],
                     res.servers.as_list())

  def test_titan_exclude_list(self):
    titans = "titan[1-3]"
    res = self.get_args(s=titans)
    self.assertEqual(res.servers.invert.as_list(),
                     ["titan4", "titan5", "titan7"])

  def test_script_name(self):
    script_name = "test1"
    res = self.get_args(script_name=script_name)
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

  def test_args(self):
    args = "a b c".split(" ")
    res = self.get_args(a=args)
    self.assertEqual(res.args, ["a", "b", "c"])

  def test_begin_time_seconds(self):
    begin_time = "10s"
    res = self.get_args(b=begin_time)
    self.assertEqual(res.begin_time, 10)

  def test_begin_time_minutes(self):
    b = "1m"
    res = self.get_args(b=b)
    self.assertEqual(res.begin_time, 60)

  def test_begin_time_hours(self):
    b = "1h"
    res = self.get_args(b=b)
    self.assertEqual(res.begin_time, 3600)

  def test_begin_time_days(self):
    b = "1d"
    res = self.get_args(b=b)
    self.assertEqual(res.begin_time, 24 * 3600)

  def test_begin_time_combined(self):
    b = "1d1h1m1s"
    res = self.get_args(b=b)
    self.assertEqual(res.begin_time, 24 * 3600 + 3600 + 61)

  def test_email_cmd_line(self):
    email = "pmc@regionh.dk"
    res = self.get_args(e=email)
    self.assertEqual(res.email, email)

  def test_email_envvar(self):
    os.environ["RHQ_EMAIL"] = "pmc@regionh.dk"
    res = self.get_args()
    self.assertEqual(res.email, "pmc@regionh.dk")

  def test_email_cmd_priority(self):
    os.environ["RHQ_EMAIL"] = "pmc@regionh.dk"
    res = self.get_args(e="pmc1@regionh.dk")
    self.assertEqual(res.email, "pmc1@regionh.dk")

  def test_priority(self):
    prio = "3"
    res = self.get_args(p=prio)
    self.assertEqual(res.priority, "3")

  def test_priority_high(self):
    prio = "5"
    res = self.get_args(p=prio)
    self.assertEqual(res.priority, "5")

  def test_priority_low(self):
    prio = "1"
    res = self.get_args(p=prio)
    self.assertEqual(res.priority, "1")

  def test_output_file_default(self):
    res = self.get_args()
    self.assertEqual(res.output_file, "my.stdout")

  def test_output_file_cmd(self):
    res = self.get_args(o="test.stdout")
    self.assertEqual(res.output_file, "test.stdout")
    
  def test_remove_job_id(self):
    job = "1234"
    res = self.get_args("remove", job_id=job)
    print(res)


if __name__ == "__main__":
  unittest.main()