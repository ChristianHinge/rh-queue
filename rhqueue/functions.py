import subprocess
import re
from multiprocessing import Pool
from typing import Dict
from .sinfo import SinfoDataGridHandler


def get_titans():
  res_str = subprocess.run("sinfo", shell=True,
                           stdout=subprocess.PIPE).stdout.decode("utf-8")
  sections = res_str.split("[")[1].split("]")[0].split(",")
  servers = []
  for section in sections:
    if "-" in section:
      servers.extend(handle_dash(section))
    else:
      servers.append(section)
  return servers


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


def handle_dash(dash_str: str):
  start_stop = list(map(int, dash_str.split("-")))
  start_stop[1] += 1
  return list(range(*start_stop))


def check_server(server):
  res = subprocess.run(f"ssh {server} nvidia-smi | grep No",
                       stdout=subprocess.PIPE,
                       shell=True)
  return (server, bool(res.stdout))


def get_open_servers(output_string):
  servers = slurm_nodelist_to_list(output_string)

  pool = Pool(7)
  vals = pool.map(check_server, servers)
  return [val[0] for val in vals if val[1]]
  # output = subprocess.run(
  #     "sinfo --Node", shell=True,
  #     stdout=subprocess.PIPE).stdout.decode("utf-8").splitlines()[:-1]
  # return SinfoDataGridHandler(output).open_titans


def slurm_nodelist_to_list(string):
  servers = []
  temp = re.findall(r"([a-zA-Z]+)(\d+|\[((\d+|(\d+-\d+)),?)+\])", string)
  for value in temp:
    name = value[0]
    if "[" == value[1][0] and "]" == value[1][-1]:
      for entry in value[1][1:-1].split(","):
        entry: str
        if "-" in entry:
          start, stop, *_ = entry.split("-")
          servers.extend(
              [*map(lambda x: f"{name}{x}", range(int(start),
                                                  int(stop) + 1))])
        else:
          servers.append(f"{name}{entry}")
    else:
      servers.append(f"{value[0]}{value[1]}")
  return servers


def handle_slurm_output(output) -> Dict[str, str]:
  values = re.findall(r"(OS)=(.+)|(\S+)=(\S+)", output)
  return {(val[2] if val[2] else val[0]): (val[3] if val[2] else val[0])
          for val in values}