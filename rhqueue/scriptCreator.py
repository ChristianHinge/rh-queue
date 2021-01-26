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
    return "ScriptLine: arg_value:{} order:{}".format(self.arg_value,
                                                      self.order)


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
    return "SBatchLine: arg_name:{}, arg_value:{}".format(
        self.arg_name, self.arg_name)


class ScriptCreatorClass(object):
  def __init__(self):
    super().__init__()
    self.script_name = "script.sh"
    self.args = []
    self.sbatch_args = []
    self.script_args = []

  def get_script_command_line(self):
    return "sbatch ./{}".format(self.script_name)

  def write_file(self):
    script = self._create_script_string()
    with open(self.script_name, "w+") as file:
      file.write(script)

  def _create_line(self, val: ScriptLine):
    if isinstance(val, SBatchLine):
      res_str = "{}={}" if "--" in val.arg_name else "{} {}"
      return res_str.format(val.arg_name, val.arg_value)
    else:
      return str(val.arg_value)

  def _create_script_string(self):
    self.args.sort()
    self.sbatch_args.sort()
    sbatch_str = "#SBATCH " + " ".join(map(self._create_line,
                                           self.sbatch_args)) + "\n"
    script = sbatch_str + "\n".join(map(self._create_line, self.args))
    
    return "#!/bin/bash\n"  + script

  def add_scriptline(self, arg_value, order):
    self.args.append(ScriptLine(arg_value, order))

  def add_sbatchline(self, arg_name, arg_value):
    self.sbatch_args.append(SBatchLine(arg_name, arg_value))