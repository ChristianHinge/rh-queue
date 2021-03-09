import re
import subprocess
import itertools


def get_servers(partition=None):
    res_str = subprocess.run("sinfo -N", shell=True,
                             stdout=subprocess.PIPE).stdout.decode("utf-8")
    servers = [i.split(" ")[0] for i in res_str.split("\n")[1:-1]]
    return set(servers)


class ServerSet(set):
    find_string = r"([a-z]+)(\[(\d)[-,]*(\d*)\]|\d)"
    def __init__(self, servers, partition=""):
        self.default_servers = set([i for i in get_servers() if partition in i])
        self._set = set(servers)
        self._partition = partition
        super().__init__(servers)

    @classmethod
    def from_slurm_list(cls, string, partition):
        servers = []
        regex = r"([a-z]+)(\[(\d+)([-,]{0,1})(\d*)\]|\d)"
        for name, first, start, range_type, stop in re.findall(regex, string):
            try:
                start = int(start)
                stop = int(stop)
            except:
                pass
            if first[0] == "[":
                if range_type:
                    for i in range(start,stop+1):
                        servers.append(f"{name}{i}")
                else:
                    servers.append(f"{name}{start}")
            else:
                servers.append(f"{name}{first}")
        return cls(servers, partition)

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
        res = ",".join(f"{k}[{self.list_to_str(v)}]"
                       for (k, v) in result.items())
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
        return ServerSet(self.default_servers - self._set, self._partition)

    def as_list(self):
        return list(sorted(self._set))

    def as_set(self):
        return self._set