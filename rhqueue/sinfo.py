from .datagrid import *


class SinfoDataGridHandler(BaseDataGridHandler):
  def __init__(self, grid) -> None:
    super().__init__(grid, SinfoDataGridLine)
  

  @property
  def open_servers(self):
    self.data: List[SinfoDataGridLine]
    return [i.id for i in self.data if i.is_open]


class SinfoDataGridLine(BaseDataGridLine):
  def __init__(self, line: List[str]) -> None:
    super().__init__(line)
    self.partition = line[2]
    self._state = line[3]

  @property
  def is_open(self) -> bool:
    return self._state == "idle"