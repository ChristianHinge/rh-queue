import getpass
import grp
import subprocess
from typing import List
from .datagrid import BaseDataGridLine, BaseDataGridHandler
from .printer import GridPrinter
from .functions import handle_slurm_output
from .servers import ServerSet


class SqueueDataGridHandler(BaseDataGridHandler):
  def __init__(self):
    super().__init__()
    self.admin = grp.getgrnam("sudo").gr_mem
    self.user = getpass.getuser()
    self.data: List[SqueueDataGridLine]

  def _to_dataline(self, line):
    return SqueueDataGridLine(self._handle_line(line))

  def get_info_about_user(self):
    ret = []
    for line in self.data:
      if line.user == self.user:
        ret.append(line)
    return ret

  def is_user_job(self, job_id):
    for line in self.data:
      if line.id == job_id and line.user == self.user:
        return True
    return False

  @property
  def is_admin(self):
    return self.user in self.admin

  def cancel_job(self, job_id):
    if self.is_user_job(job_id):
      subprocess.call(["scancel {}".format(job_id)], shell=True)
    elif self.is_admin:
      subprocess.call(["sudo -u slurm scancel {}".format(job_id)], shell=True)
    else:
      print("You do not have the permission to cancel that job")


class SqueueDataGridLine(BaseDataGridLine):
  def __init__(self, line: List[str]) -> None:
    super().__init__(line)
    self._data = line
    self.partition = line[1]
    self._script_name = None
    self.user = line[3]
    self._state = line[4]
    self.time = line[5]
    self.nodes = line[6]
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
      self._nodelist = val.to_slurm_list()
    return self._nodelist
  
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
    return {"R": "Running", "PD": "In Queue", "ST": "State"}[self._state]

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


class SqueueDataGridPrinter(BaseDataGridHandler):
  def __init__(self):
    super().__init__()
    self.data: List[SqueueDataGridLine]

  def _to_dataline(self, line):
    return SqueueDataGridLine(self._handle_line(line))



  def print_vals(self, job_id=None, verbosity=None, columns=[]):


    if columns:
      self.print_info(columns)
    else:
      res = subprocess.run(f"scontrol show jobs {job_id}",
                           shell=True,
                           stdout=subprocess.PIPE)
      if res.returncode != 0:
        print("there was a problem getting the job")
      else:
        keys = [
            "EligibleTime", "SubmitTime", "StartTime", "ExcNodeList", "JobId",
            "JobName", "JobState", "StdOut", "UserId", "WorkDir", "NodesList"
        ]
        output = handle_slurm_output(res.stdout.decode("utf-8"))

        if verbosity < 2:
          verbosity_dict = {i: output[i] for i in output.keys() if i in keys}
        else:
          verbosity_dict = output
        GridPrinter([
            sorted([list(j) for j in verbosity_dict.items()],
                   key=lambda x: x[0])
        ],
                    headers=[["Key", "Value"]],
                    title=f"Information about job:{job_id}")

  def print_info(self, columns):

    self.colmn_sort = [(idx, val) for idx, val in enumerate(columns)]
    self.num_columns = len(columns)
    header_string = self._get_columns(self.headers, columns)
    header_string = list(
        map(lambda x: x.replace("(REASON)", ""), header_string))
    running_lines = []
    waiting_lines = []
    title = "Queue Information"
    sections = ["Running Items", "Items in Queue"]
    for value in self.data:
      if value.state == "Running":
        running_lines.append(self._get_columns(value, columns))
      elif value.state == "In Queue":
        waiting_lines.append(self._get_columns(value, columns))
    headers = [header_string, header_string]
    data = [running_lines, waiting_lines]
    GridPrinter(data, title=title, sections=sections, headers=headers)

  def _get_columns(self, line: List[str], columns) -> List[str]:
    ret = []
    for i, value in enumerate(line):
      if i in columns:
        ret.append(str(value))
    return list(
        map(lambda x: x[1],
            sorted((self.colmn_sort[i][1], ret[i]) for i in range(len(ret)))))
