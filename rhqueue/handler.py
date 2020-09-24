import subprocess
import os
from .scriptCreator import ScriptCreatorClass
from .squeue import *
from .functions import *


class RHQueueHander:
  processor = ScriptCreatorClass()

  def __init__(self, parser) -> None:
    if parser.args.command is None:
      print("No Arguments were given")
      parser.parser.print_help()
      exit(1)

    if not hasattr(self, parser.args.command):
      print("The argument given was not found")
      parser.print_help()
      exit(1)
    getattr(self, parser.args.command)(parser.args)

  def remove(self, args):
    data = SqueueDataGridHandler()
    data.cancel_job(args.job[0])

  def queue(self, args):

    args.script_name = args.script_name if args.script_name else args.script

    self.processor.add_scriptline(
        "srun -n1 {} {}".format(os.path.abspath(args.script),
                                " ".join(args.args)), 0)

    self.processor.add_scriptline("export PYTHONUNBUFFERED=1", -10)

    # base sbatch arguments
    self.processor.add_scriptline("chmod +x {}".format(args.script), -2)
    self.processor.add_sbatchline("--priority", args.priority)
    self.processor.add_sbatchline("--ntasks", "1")
    self.processor.add_sbatchline("--gres", "gpu:titan:1")
    self.processor.add_sbatchline("-o", args.output_file)
    self.processor.add_sbatchline(
        "--job-name", args.script_name if args.script_name else args.script)

    if args.begin_time:
      self.processor.add_sbatchline("--begin",
                                    "now+{}".format(args.begin_time))

    # Handle Email
    if args.email:
      self.processor.add_scriptline(
          f"rhqemail start {args.email} {os.path.abspath(args.script)} {' '.join(args.args)}",
          -5)
      end_str = "if [[ $? -eq 0 ]]; then\n" + "  rhqemail completed {0} {1} {2}\n" + "else\n" + " rhqemail failed {0} {1} {2}\n" + "fi\n"
      self.processor.add_scriptline(
          end_str.format(args.email, os.path.abspath(args.script), ' '.join(args.args)), 2)

    #Handle venv
    if args.venv:
      self.processor.add_scriptline("source {}/bin/activate".format(args.venv),
                                    -1)
      self.processor.add_scriptline("deactivate", 1)

    if args.conda_venv:
      self.processor.add_scriptline(
          "conda activate {}".format(args.conda_venv), -1)
      self.processor.add_scriptline("conda deactivate", 1)

    if args.servers:
      self.processor.add_sbatchline("-x", ",".join(args.servers.invert))

    
    self.processor.write_file()

    if args.test:
      print(args)
    else:
      subprocess.call(["chmod +x {}".format(args.script)],
                      stdout=subprocess.PIPE,
                      shell=True)
      res = subprocess.run(self.processor.get_script_command_line(),
                           stdout=subprocess.PIPE,
                           shell=True)
      subprocess.call(["rm ./script.sh"], stdout=subprocess.PIPE, shell=True)
      exit(res.returncode)

  def info(self, args):
    info = SqueueDataGridPrinter()
    if args.job_id:
      info.print_extra_information(args.job_id, args.verbosity)
    else:
      info.print_vals(0, 3, 2, 5, 7)