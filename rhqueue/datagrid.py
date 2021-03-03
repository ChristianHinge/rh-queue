from typing import List
import subprocess
from .servers import ServerSet
from .functions import handle_slurm_output
from collections import OrderedDict


class DataGridLine(object):
  def __init__(self, id: int, data=None) -> None:
    self.info = data or self.get_job_by_id(id)
    self.info["User"] = self.info["UserId"].split("(")[0]
    self.info["Id"] = self.info["JobId"]
    self._script_name = None
    self._nodelist = None

  @property
  def id(self):
    return int(self.info["JobId"])

  def user(self):
    return self.info["User"]

  @property
  def script_name(self):
    if self._script_name is None:
      self._script_name = self.info["JobName"]
    return self._script_name

  @property
  def nodelist(self):
    if self._nodelist is None:
      if self.info["NodeList"] == "(null)":
        val = ServerSet.from_slurm_list(self.info["ExcNodeList"]).invert
      else:
        val = ServerSet.from_slurm_list(self.info["NodeList"])
      self._nodelist = val
    return self._nodelist.to_slurm_list()

  def get_job_by_id(self, job_id):
    output = subprocess.run(f"scontrol show jobs {job_id}",
                            shell=True,
                            stdout=subprocess.PIPE).stdout.decode("utf-8")
    ret = handle_slurm_output(output)
    return ret

  @property
  def is_running(self):
    return self.info["JobState"] == "RUNNING"

  @property
  def is_queued(self):
    return self.info["JobState"] == "PENDING"

  def __getitem__(self, s: int):
    if s == "Name":
      return self.script_name
    if s == "NodeList" or s == "NodesList":
      return self.nodelist
    return self.info[s]

  def get_from_keys(self, keys):
    ret = OrderedDict()
    for k in keys:
      ret[k] = self[k]
    # ret = [self[k] for k in keys]
    return ret


class DataGridHandler(object):
  def __init__(self, data=None) -> None:
    self.data: List[DataGridLine]
    self.options = [
        "JobID", "Partition", "Name", "UserName", "StateCompact", "TimeUsed",
        "NumNodes", "ReasonList", "PriorityLong"
    ]
    grid = data or subprocess.run(
        f"squeue -O 'JobID'", stdout=subprocess.PIPE,
        shell=True).stdout.decode("utf-8").split("\n")[1:-1]
    grid = [i.split()[0] for i in grid]
    self.data = [self._to_dataline(id) for id in grid[1:]]

  def _to_dataline(self, id_val):
    return DataGridLine(id_val)

  def get_user_jobs(self, user):
    return [line for line in self.data if line.user == user]

  def is_user_job(self, user, job_id):
    return job_id in [line.id for line in self.get_user_jobs(user)]

  def __getitem__(self, k):
    if isinstance(k, str):
      return [i.info[k] for i in self.data]
    if isinstance(k, int):
      return self.data[k]
    if isinstance(k, tuple) and len(k) == 2:
      return self.__getitem__(k[0])[k[1]]
    else:
      raise Exception(f"incorrect keys:{k}")


  def __len__(self) -> int:
    return len(self.data)

  @property
  def running_items(self):
    return [i for i in self.data if i.is_running]

  @property
  def queued_items(self):
    return [i for i in self.data if i.is_queued]
  
  def from_id(self, id):
    return next((i for i in self.data if i.id == id or i["Id"] == id), None)