import re
import subprocess


def handle_dash(dash_str: str):
  start_stop = list(map(int, dash_str.split("-")))
  start_stop[1] += 1
  return list(range(*start_stop))


def get_servers():
  res_str = subprocess.run("sinfo", shell=True,
                           stdout=subprocess.PIPE).stdout.decode("utf-8")
  sections = res_str.split("[")[1].split("]")[0].split(",")
  servers = []
  for section in sections:
    if "-" in section:
      servers.extend(handle_dash(section))
    else:
      servers.append(section)
  return set(servers)


class ServerSet(set):
  default_servers = get_servers()

  def __init__(self, servers):
    self._set = set(servers)
    super().__init__(servers)

  @classmethod
  def from_slurm_list(cls, string):
    servers = []
    temp = re.findall(r"([a-zA-Z]+)(\d+|\[((\d+|(\d+-\d+)),?)+\])", string)
    for value in temp:
      name = value[0]
      if "[" == value[1][0] and "]" == value[1][-1]:
        for entry in value[1][1:-1].split(","):
          entry: str
          if "-" in entry:
            start, stop, *_ = entry.split("-")
            servers.extend([
                *map(lambda x: f"{name}{x}", range(int(start),
                                                   int(stop) + 1))
            ])
          else:
            servers.append(f"{name}{entry}")
      else:
        servers.append(f"{value[0]}{value[1]}")
    return cls(servers)

  @property
  def invert(self):
    self._set = self.default_servers - self._set
    return self

  def as_list(self):
    return list(sorted(self._set))
