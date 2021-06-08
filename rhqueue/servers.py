import re
import subprocess
import itertools


def get_servers(partition=None):
    command = "sinfo -N" if partition is None else f"sinfo -N -p {partition}"
    res_str = subprocess.run(command, shell=True,
                             stdout=subprocess.PIPE).stdout.decode("utf-8")
    data = [i.split(" ") for i in res_str.split("\n")[1:-1]]
    servers = []
    for server, _, part, _ in [(j for j in i if j) for i in data]:
        if partition is None and part[-1] == "*":
            servers.append(server)
        elif partition is not None:
            servers.append(server)
    return servers


class ServerSet(set):

    def __init__(self, servers, partitions=[]):
        default_servers = set(p for partition in partitions
                              for p in get_servers(partition))
        if len(servers) == 0:
            self.default_servers = set(get_servers())
        else:
            self.default_servers = default_servers
        self._set = set(servers)
        self._partition = partitions
        super().__init__(servers)

    @classmethod
    def from_slurm_list(cls, string:str):
        """Builds the ServerSet based on the string passed to the function

        Args:
            string (str): the string to build the set from

        Returns:
            ServerSet: The ServerSet from the string passed
        """
        servers = []
        partition = []
        regex = r"([a-z]+)(\[(\d+,?|\d+[-]\d*)+\]|\d)"
        for name, whole, _ in re.findall(regex, string):
            partition.append(name)
            inner_regex = r"((\d+)-?(\d+)?)+"
            for _, start, stop in re.findall(inner_regex, whole):
            
                try:
                    start = int(start)
                    stop = int(stop)
                except:
                    start = int(start)
                    stop = int(start)
                for i in range(start, stop + 1):
                        servers.append(f"{name}{i}")
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