from typing import List

class BaseDataGridLine(list):
  def __init__(self, line: List[str]) -> None:
    super().__init__(line)
    self._data = line
    try:
      self.id = int(line[0])
    except Exception as e:
      self.id = line[0]
    


class BaseDataGridHandler(list):
  def __init__(self, grid, dataline_class =BaseDataGridLine) -> None:
    self.dataline_class = dataline_class
    self.headers = self._to_dataline(grid[0])
    self.data = []
    for line in grid[1:]:
      self.data.append(self._to_dataline(line))
    super().__init__([self.headers, *self.data])
    
  def _handle_line(self, line: str):
    return [data for data in line.split(" ") if data]

  def _to_dataline(self, line):
    return self.dataline_class(self._handle_line(line))