import re
import subprocess
import itertools


def handle_dash(dash_str: str):
  start_stop = list(map(int, dash_str.split("-")))
  start_stop[1] += 1
  return list(range(*start_stop))


def get_servers():
  res_str = subprocess.run("sinfo -N", shell=True,
                           stdout=subprocess.PIPE).stdout.decode("utf-8")
  servers = [i.split(" ")[0] for i in res_str.split("\n")[1:-1]]
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

  def to_slurm_list(self):
    if "[" not in str(self._set) and "]" not in str(
        self._set) and "," not in str(self._set):
      return "".join(self._set)
    lst = [re.findall(r"(([a-zA-Z]+)(\d+))(,?)", i)[0] for i in self._set]
    lst = [(i[1], i[2]) for i in lst]
    result = {
        k: list(self.ranges(int(i[1]) for i in g))
        for k, g in itertools.groupby(sorted(lst), key=lambda x: x[0])
    }
    res = ",".join(f"{k}[{self.list_to_str(v)}]" for (k, v) in result.items())
    return res

  def list_to_str(self, iterable):
    return ",".join(f"{i[0]}-{i[1]}" if i[0] != i[1] else str(i[0])
                    for i in iterable)

  def ranges(self, i):
    for a, b in itertools.groupby(enumerate(i),
                                  lambda pair: pair[1] - pair[0]):
      b = list(b)
      yield b[0][1], b[-1][1]


  @property
  def invert(self):
    return ServerSet(self.default_servers - self._set)

  def as_list(self):

    return list(sorted(self._set))

  def as_set(self):
    return self._set
