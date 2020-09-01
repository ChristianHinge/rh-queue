import getpass
import grp
import subprocess
from typing import List
from .datagrid import BaseDataGridLine, BaseDataGridHandler
from .printer import SqueueDataGridPrinter, GridPrinter
from .functions import handle_slurm_output


class SqueueDataGridHandler(BaseDataGridHandler):
  def __init__(self):
    output = subprocess.run("squeue", stdout=subprocess.PIPE,
                            shell=True).stdout.decode("utf-8").split("\n")[:-1]
    self.admin = grp.getgrnam("sudo").gr_mem
    super().__init__(output, SqueueDataGridLine)
    self.user = getpass.getuser()

  def print_vals(self, spacing, *args):
    SqueueDataGridPrinter(self.headers, self.data, spacing, *args)

  def print_extra_information(self, job_id):
    res = subprocess.run(f"scontrol show jobs -dd {job_id}",
                         shell=True,
                         stdout=subprocess.PIPE)
    if res.returncode != 0:
      print("there was a problem getting the job")
    else:
      output = handle_slurm_output(res.stdout.decode("utf-8"))
      GridPrinter([sorted(list(output.items()),key=lambda x:x[0])],headers=[["Key", "Value"]],
                  title=f"Information about job:{job_id}")

  def get_info_about_user(self):
    ret = []
    for line in self.data:
      if line.user == self.user:
        ret.append(line)
    return ret

  def get_line_by_job_id(self, job_id):
    for line in self.data:
      if line.id == job_id:
        return line
    return None

  def is_user_job(self, job_id):
    for line in self.data:
      if (line.user == self.user
          or self.user in self.admin) and line.id == job_id:
        return True
    return False

  def cancel_job(self, job_id):
    if self.is_user_job(job_id) and self.get_line_by_job_id(
        job_id) is not None:
      subprocess.call(["scancel {}".format(job_id)], shell=True)
    else:
      print("You do not have the permission to cancel that job")


class SqueueDataGridLine(BaseDataGridLine):
  def __init__(self, line: List[str]) -> None:
    super().__init__(line)
    self.partition = line[1]
    self.script = line[2]
    self.user = line[3]
    self._state = line[4]
    self.time = line[5]
    self.nodes = line[6]
    self.nodelist = line[7]

  @property
  def state(self):
    return {"R": "Running", "PD": "In Queue", "ST": "State"}[self._state]

  def __getitem__(self, s: int):
    if s == 4:
      return self.state
    return self._data[s]

  def __iter__(self):
    for idx in range(len(self._data)):
      yield self[idx]