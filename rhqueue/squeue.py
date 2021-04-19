import getpass
import grp
import subprocess
from typing import List
from .datagrid import DataGridLine, DataGridHandler
from .printer import GridPrinter


class SqueueDataGridHandler:
    def __init__(self):
        super().__init__()
        self.admin = grp.getgrnam("sudo").gr_mem
        self.user = getpass.getuser()
        self.data = DataGridHandler()

    @property
    def is_user_admin(self):
        return self.user in self.admin

    def cancel_job(self, job_id):
        if self.data.is_user_job(self.user, job_id):
            self.cancel_check("scancel {}", job_id)
        elif self.is_user_admin:
            self.cancel_check("sudo -u slurm scancel {}", job_id)
        else:
            print("You do not have the permission to cancel that job")

    def cancel_check(self, cancel_command_struct, job_id):

        valid = {"yes": True, "y": True, "no": False, "n": False}
        while True:
            choice = input(f"Do you wish delete {job_id}? [y/n]").lower()
            if choice in valid:
                res = valid[choice]
                break
            else:
                print("Please respond with 'yes' or 'no' "
                      "(or 'y' or 'n').\n")
        if res:
            subprocess.call([cancel_command_struct.format(job_id)], shell=True)
        else:
            print("cancelled script removal")
            exit(0)

    def print_vals(self, job_id=None, verbose=False, columns=[]):
        if columns:
            self.print_info(columns)
        else:
            keys = [
                "EligibleTime", "SubmitTime", "StartTime", "ExcNodeList",
                "JobId", "JobName", "JobState", "StdOut", "UserId", "WorkDir",
                "NodeList"
            ]
            output = self.data.get_job_from_id(job_id)
            output = output.info if verbose else output.get_from_keys(keys)
            GridPrinter([
                sorted([list(j) for j in output.items()], key=lambda x: x[0])
            ],
                        headers=[["Key", "Value"]],
                        title=f"Information about job:{job_id}")

    def print_info(self, columns):
        item_lists = [self.data.running_items, self.data.queued_items]
        data = [[self._get_columns(value, columns) for value in items]
                for items in item_lists]
        headers = [columns] * len(data)
        GridPrinter(data,
                    title="Queue Information",
                    sections=["Running Items", "Items in Queue"],
                    headers=headers)

    def _get_columns(self, line: DataGridLine, columns) -> List[str]:
        return list(line.get_from_keys(columns).values())
