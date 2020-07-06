class ScriptLine(object):
  def __init__(self, arg_value, order):
    super().__init__()
    self.arg_value = arg_value
    self.order = order

  def __lt__(self, other):
    if type(other) == ScriptLine:
      return self.order < other.order
    if type(other) == SBatchLine:
      return False
      
  def __repr__(self):
    return "ScriptLine: arg_value:{} order:{}".format(self.arg_value, self.order)

class SBatchLine(ScriptLine):
  def __init__(self, arg_name, arg_value):
    super().__init__(arg_value, 0)
    self.arg_name = arg_name
  
  def __lt__(self, other):
    if type(other) == SBatchLine:
      return self.arg_name < other.arg_name
    if type(other) == ScriptLine:
      return True

  def __repr__(self):
    return "SBatchLine: arg_name:{}, arg_value:{}".format(self.arg_name, self.arg_name)
  
class ScriptCreatorClass(object):
  script_name = "script.sh"
  def __init__(self):
    super().__init__()
    self.args = []
    self.sbatch_args = []
    self.script_args = []

  def write_file(self):
    script = self.create_script()
    with open(self.script_name, "w+") as file:
      file.write(script)

  def _create_line(self, val:ScriptLine):
    if isinstance(val, SBatchLine):
      res_str = "{}={}" if "--" in val.arg_name else "{} {}"
      return res_str.format(val.arg_name, val.arg_value)
    else:
      return str(val.arg_value)
  
  def create_script(self):
    self.args.sort()
    self.sbatch_args.sort()
    sbatch_str = "#SBATCH " + " ".join(map(self._create_line, self.sbatch_args)) + "\n"
    script = sbatch_str + "\n".join(map(self._create_line, self.args))
    return "#!/bin/bash\n" + script

  def add_scriptline(self, arg_value, order):
    self.args.append(ScriptLine(arg_value, order))

  def add_sbatchline(self, arg_name, arg_value):
    self.sbatch_args.append(SBatchLine(arg_name, arg_value))
  
class DataGrid(object):

  def __init__(self, output):
    self.admin = ["pmcd"]
    self.headers = self._handle_line(output[0])
    self.data:List[DataGridLine] = []
    self.user = getpass.getuser()
    for line in output[1:]:
      self.data.append(self._to_dataline(line))

  def _handle_line(self, line):
    line = line.decode()
    return [data for data in line[:-1].split(" ") if data]

  def _to_dataline(self, line):
    return DataGridLine(self._handle_line(line))

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
      if (line.user == self.user or
          self.user in self.admin) and line.id == job_id:
        return True
    return False

  def cancel_job(self, job_id):
    if self.is_user_job(job_id) and self.get_line_by_job_id(job_id) is not None:
      job_res_id = self.get_line_by_job_id(job_id).id
      subprocess.call(["scancel {}".format(job_id)], shell=True)
    else:
      print("You do not have the permission to cancel that job")