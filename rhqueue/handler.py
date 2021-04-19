import subprocess
import os
from .scriptCreator import ScriptCreatorClass
from .squeue import *
from .functions import *
import sys


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
        data.cancel_job(args.job)

    def check_shebang(self, file_path):
        out = subprocess.run(f"head -1 {file_path}",
                             shell=True,
                             stdout=subprocess.PIPE)
        shebang = out.stdout.decode("utf-8").strip("\n")
        if "#!" not in shebang:
            print("there is no shebang defined a recommended shebang is:\n" +
                  "\"#!/usr/bin/env python3\"")
            exit(3)
        if not "#!/usr/bin/env python3" in shebang:
            print("The recommened shebang is:\n" +
                  "\"#!/usr/bin/env python3\"")
            exit(3)

    def queue(self, args):

        self.check_shebang(args.script)
        # self.processor.add_scriptline(f"echo '{sys.argv}'", -16)
        # self.processor.add_scriptline(f"head -1 {args.script}", -15)
        # self.processor.add_scriptline("printenv", -14)
        self.processor.add_scriptline(
            "srun -n1 {} {}".format(os.path.abspath(args.script),
                                    " ".join(args.args)), 0)
        self.processor.add_scriptline("export PYTHONUNBUFFERED=1", -10)

        # base sbatch arguments

        self.processor.add_scriptline("chmod +x {}".format(args.script), -2)
        self.processor.add_sbatchline("--ntasks", "1")
        self.processor.add_sbatchline("--gres", "gpu:titan:1")
        self.processor.add_sbatchline("-o", args.output_file)
        self.processor.add_sbatchline(
            "--job-name",
            args.script_name if args.script_name else args.script)

        if args.begin_time:
            self.processor.add_sbatchline("--begin",
                                          "now+{}".format(args.begin_time))

        # Handle Email
        if args.email:
            self.processor.add_scriptline(
                f"export SLURM_OUTPUT_FILE='{args.output_file}'", -9)
            self.processor.add_scriptline(
                f"export SLURM_SCRIPT='{os.path.abspath(args.script)}'", -8)
            self.processor.add_scriptline(
                f"export SLURM_SCRIPT_ARGS='{' '.join(args.args)}'", -8)
            self.processor.add_scriptline(
                f"export SLURM_SCRIPT_EMAIL='{args.email}'", -8)
            self.processor.add_scriptline("rhqemail start", -5)
            end_str = ("if [[ $? -eq 0 ]]; then\n" + "  rhqemail completed\n" +
                       "else\n" + " rhqemail failed\n" + "fi\n")
            self.processor.add_scriptline(end_str, 2)

        #Handle venv
        if args.venv:
            self.processor.add_scriptline(
                "source {}/bin/activate".format(args.venv), -1)
            self.processor.add_scriptline("deactivate", 1)

        if args.condaVenv:
            self.processor.add_scriptline("source ~/.bashrc", -20)
            self.processor.add_scriptline(
                "conda activate {}".format(args.condaVenv), -1)
            self.processor.add_scriptline("conda deactivate", 1)

        if args.servers and args.servers.invert:
            self.processor.add_sbatchline("-x", ",".join(args.servers.invert))
        if args.source_script:
            self.processor.add_scriptline(f"source {args.source_script}", -20)

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
            subprocess.call(["rm ./script.sh"],
                            stdout=subprocess.PIPE,
                            shell=True)
            full = res.stdout.decode("utf-8")[:-1]
            id_val = full.split()[-1]
            subprocess.call(
                [f"scontrol update jobid={id_val} priority={args.priority}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True)
            print(full)
            exit(res.returncode)

    def info(self, args):
        info = SqueueDataGridHandler()
        if args.job_id:
            info.print_vals(job_id=args.job_id, verbose=args.verbose)
        else:
            info.print_vals(columns=[
                "Id", "User", "JobName", "RunTime", "NodeList", "Priority"
            ])
