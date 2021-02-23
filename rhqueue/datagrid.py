from typing import List
import subprocess
from .servers import ServerSet
from .functions import handle_slurm_output


class DataGridLine(list):
  def __init__(self, line: List[str]) -> None:
    super().__init__(line)
    self._data = line
    try:
      self.id = int(line[0])
    except:
      self.id = None
    self._script_name = None
    self._state = line[4]
    self._nodelist = None
    self._info = None

  @property
  def script_name(self):
    if self._script_name is None:
      if self.info is None:
        self._script_name = self._data[2]
      else:
        self._script_name = self.info["JobName"]
    return self._script_name

  @property
  def nodelist(self):
    if self.info is None:
      return self._data[7]
    if self._nodelist is None:
      if self.info["NodeList"] == "(null)":
        val = ServerSet.from_slurm_list(self.info["ExcNodeList"]).invert
      else:
        val = ServerSet.from_slurm_list(self.info["NodeList"])
      self._nodelist = val
    return self._nodelist.to_slurm_list()

  @property
  def info(self):
    if self._info is None and isinstance(self.id, int):
      self._info = self.get_job_by_id(self.id)
    return self._info

  def get_job_by_id(self, job_id):
    output = subprocess.run(f"scontrol show jobs {job_id}",
                            shell=True,
                            stdout=subprocess.PIPE).stdout.decode("utf-8")
    ret = handle_slurm_output(output)
    return ret

  @property
  def state(self):
    return {
        "R": "Running",
        "PD": "In Queue",
        "ST": "State",
        "CG": "Completing"
    }[self._state]

  def __getitem__(self, s: int):
    if s == 4:
      return self.state
    if s == 2:
      return self.script_name
    if s == 7:
      return self.nodelist
    return self._data[s]

  def __iter__(self):
    for idx in range(len(self._data)):
      yield self[idx]


class DataGridHandler(list):
  def __init__(self) -> None:
    self.data: List[DataGridLine]
    options = [
        "JobID", "Partition", "Name", "UserName", "StateCompact", "TimeUsed",
        "NumNodes", "ReasonList", "PriorityLong"
    ]
    options[-1] += ":.100"
    grid = subprocess.run(
        f"squeue -O '{':.100,'.join(options)}'",
        stdout=subprocess.PIPE,
        shell=True).stdout.decode("utf-8").split("\n")[:-1]
    self.headers = self._to_dataline(grid[0])
    self.data = []
    for line in grid[1:]:
      self.data.append(self._to_dataline(line))
    super().__init__([self.headers, *self.data])

  def _handle_line(self, line: str):
    return [data for data in line.split(" ") if data]

  def _to_dataline(self, line):
    return DataGridLine(self._handle_line(line))