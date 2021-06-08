import subprocess
import re
from typing import Dict


def parse_time(begin_string):
    ret_seconds = 0
    for i in re.findall(r"(\d+d)?(\d+h)?(\d+m)?(\d+s)?", begin_string)[0]:
        if i:
            case = i[-1]
            value = int(i[:-1])
            if "d" in case:
                ret_seconds += value * 60 * 60 * 24
            if "h" in case:
                ret_seconds += value * 60 * 60
            if "m" in case:
                ret_seconds += value * 60
            if "s" in case:
                ret_seconds += value
    return ret_seconds


def check_server(server):
    res = subprocess.run(f"ssh {server} nvidia-smi | grep No",
                         stdout=subprocess.PIPE,
                         shell=True)
    return (server, bool(res.stdout))


def get_open_servers(output_string):
    from rhqueue.servers import ServerSet
    from multiprocessing import Pool
    servers = ServerSet.from_slurm_list(output_string).as_list()
    pool = Pool(7)
    vals = pool.map(check_server, servers)
    return [val[0] for val in vals if val[1]]


def handle_slurm_output(output) -> Dict[str, str]:
    values = re.findall(r"(OS)=(.+)|(\S+)=(\S+)", output)
    return {(val[2] if val[2] else val[0]): (val[3] if val[2] else val[0])
            for val in values}
