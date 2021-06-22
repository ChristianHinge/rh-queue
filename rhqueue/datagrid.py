from typing import List
import subprocess
from .functions import handle_slurm_output



class DataGridLine(object):
    def __init__(self, id=None, data=None) -> None:
        self.info = data or self.get_job_by_id(id)
        self.info["User"] = self.info["UserId"].split("(")[0]
        self.info["Id"] = self.info["JobId"]
        try:
            comment = {
                i.split(":")[0]: i.split(":")[1]
                for i in self.info["Comment"].split(",")
            }
            self.info = {**self.info, **comment}
            del self.info["Comment"]
        except:
            pass
        self._script_name = None
        self._nodelist = None

    @property
    def id(self):
        return int(self.info["JobId"])

    @property
    def user(self):
        return self.info["User"]

    @property
    def priority(self):
        return self.info["Priority"]

    @property
    def script_name(self):
        if self._script_name is None:
            self._script_name = self.info["JobName"]
        return self._script_name

    @property
    def nodelist(self):
        from .servers import ServerSet
        if self._nodelist is None:
            if self.info["NodeList"] == "(null)":
                val = ServerSet.from_slurm_list(
                    self.info["ExcNodeList"]).invert
            else:
                val = ServerSet.from_slurm_list(self.info["NodeList"])
            self._nodelist = val
        return self._nodelist.to_slurm_list()

    def get_job_by_id(self, job_id):
        output = subprocess.run(f"scontrol show jobs {job_id}",
                                shell=True,
                                stdout=subprocess.PIPE).stdout.decode("utf-8")
        ret = handle_slurm_output(output)
        return ret

    @property
    def is_running(self):
        return self.info["JobState"] == "RUNNING"

    @property
    def is_queued(self):
        return self.info["JobState"] == "PENDING"

    def __getitem__(self, s: str):
        if s == "Name":
            return self.script_name
        if s == "NodeList":
            return self.nodelist
        return self.info[s]

    def get_from_keys(self, keys):
        from collections import OrderedDict
        ret = OrderedDict()
        for k in keys:
            ret[k] = self[k]
        return ret

    def __repr__(self) -> str:
        return f"Job:jobID={self.id}, user={self.user}, name={self.script_name}, server={self.nodelist}"


class JobNotFoundException(Exception):
    pass


class DataGridHandler(object):
    def __init__(self, data=None) -> None:
        self.data: List[DataGridLine]
        grid = data or subprocess.run(
            "scontrol show jobs", stdout=subprocess.PIPE,
            shell=True).stdout.decode("utf-8").split("\n\n")[:-1]
        self.data = [
            DataGridLine(data=handle_slurm_output(data)) for data in grid
        ]
        self.data.sort(key=lambda x: x.priority, reverse=True)

    def get_user_jobs(self, user):
        return [line for line in self.data if line.user == user]

    def is_user_job(self, user, job_id):
        return job_id in [line.id for line in self.get_user_jobs(user)]

    def __getitem__(self, k):
        if isinstance(k, str):
            return [i.info[k] for i in self.data]
        if isinstance(k, int):
            return self.data[k]
        if isinstance(k, tuple) and len(k) == 2:
            return self.__getitem__(k[0])[k[1]]
        else:
            raise Exception(f"incorrect keys:{k}")

    def __len__(self) -> int:
        return len(self.data)

    @property
    def running_items(self):
        return [i for i in self.data if i.is_running]

    @property
    def queued_items(self):
        return [i for i in self.data if i.is_queued]

    def get_job_from_id(self, job_id):
        try:
            return next((i for i in self.data if i.id == job_id))
        except:
            raise JobNotFoundException(f"uable to find the job {id}")
