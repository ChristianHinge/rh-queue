import getpass
import grp
import subprocess
from typing import List
from .datagrid import DataGridLine, DataGridHandler
from .printer import GridPrinter


class SqueueDataGridHandler(DataGridHandler):
    def __init__(self):
        super().__init__()
        self.admin = grp.getgrnam("sudo").gr_mem
        self.user = getpass.getuser()

    @property
    def is_user_admin(self):
        return self.user in self.admin

    def cancel_job(self, job_id):
        if self.is_user_job(self.user, job_id):
            subprocess.call(["scancel {}".format(job_id)], shell=True)
        elif self.is_user_admin:
            subprocess.call(["sudo -u slurm scancel {}".format(job_id)],
                            shell=True)
        else:
            print("You do not have the permission to cancel that job")

    def print_vals(self, job_id=None, verbose=False, columns=[]):
        if columns:
            self.print_info(columns)
        else:
            keys = [
                "EligibleTime", "SubmitTime", "StartTime", "ExcNodeList",
                "JobId", "JobName", "JobState", "StdOut", "UserId", "WorkDir",
                "NodeList"
            ]
            output = self.from_id(job_id)
            output = output.info if verbose else output.get_from_keys(keys)
            GridPrinter([
                sorted([list(j) for j in output.items()], key=lambda x: x[0])
            ],
                        headers=[["Key", "Value"]],
                        title=f"Information about job:{job_id}")

    def print_info(self, columns):
        item_lists = [self.running_items, self.queued_items]
        data = [[self._get_columns(value, columns) for value in items]
                for items in item_lists]
        headers = [columns] * len(data)
        GridPrinter(data,
                    title="Queue Information",
                    sections=["Running Items", "Items in Queue"],
                    headers=headers)

    def _get_columns(self, line: DataGridLine, columns) -> List[str]:
        return list(line.get_from_keys(columns).values())
