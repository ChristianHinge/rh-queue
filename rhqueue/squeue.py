import subprocess
from typing import List
from .datagrid import DataGridLine


class SqueueDataGridHandler:
    def __init__(self):
        super().__init__()
        import getpass
        import grp
        # get users in sudo group
        self.admin = grp.getgrnam("sudo").gr_mem
        # get current user
        self.user = getpass.getuser()
        from .datagrid import DataGridHandler
        # load the data from the queue
        self.data = DataGridHandler()

    def is_user_admin(self):
        return self.user in self.admin

    def cancel_job(self, job_id: str):
        """function used to cancel a job, first getting the job from the queue, 
        then checking if the user created the job or the user is part of sudo.
        Following this will pass the job to the cancel check function

        Args:
            job_id (str): the id of the job to be cancelled
        """
        # get the current job by id
        job = self.data.get_job_from_id(job_id)
        if self.data.is_user_job(self.user, job):
            self.cancel_check("scancel {id}", job)
        elif self.is_user_admin():
            self.cancel_check("sudo -u slurm scancel {id}", job)
        else:
            print("You do not have the permission to cancel that job")

    def cancel_check(self, cancel_command_struct: str, job_id: DataGridLine):
        """Function that confirms if the use wants to delete from the string for how to call the deletion funciton

        Args:
            cancel_command_struct (str): the command string for how to delete the job
            job_id (DataGridLine): the id of the job to be cancelled
        """
        valid = {"yes": True, "y": True, "no": False, "n": False}
        print(f"job ID: {job_id}")
        while True:
            choice = input(
                f"Do you wish delete job {job_id.id}? [y/n]").lower()
            if choice in valid:
                res = valid[choice]
                break
            else:
                print("Please respond with 'yes' or 'no' "
                      "(or 'y' or 'n').\n")
        if res:
            subprocess.call([cancel_command_struct.format(id=job_id.id)],
                            shell=True)
        else:
            print("cancelled script removal")
            exit(0)
    
    def print_vals(self, job_id:str=None, verbose:bool=False, columns:List[str]=[]):
        from .printer import GridPrinter
        if columns:
            item_lists = [self.data.running_items, self.data.queued_items]
            data = [[list(value.get_from_keys(columns).values()) for value in items]
                    for items in item_lists]
            headers = [columns] * len(data)
            GridPrinter(data,
                        title="Queue Information",
                        sections=["Running Items", "Items in Queue"],
                        headers=headers)
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