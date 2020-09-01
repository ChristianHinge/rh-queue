from typing import List
from rhprinter import bcolors


class SqueueDataGridPrinter(object):
  def __init__(self, headers, data, spacing, *columns):
    self.spacing = spacing + 2
    self.data = data
    self.headers = headers
    self.columns = columns
    self.colmn_sort = [(idx, val) for idx, val in enumerate(self.columns)]
    self.num_columns = len(columns)
    header_string = self._get_columns(self.headers, center=True)
    self.line_width = len(columns) * (self.spacing + 1) + 1
    running_lines = []
    waiting_lines = []
    title = "Queue Information"
    sections = ["Running Items", "Items in Queue"]
    for value in self.data:
      if value.state == "Running":
        running_lines.append(self._get_columns(value))
      elif value.state == "In Queue":
        waiting_lines.append(self._get_columns(value))
    headers = [header_string, header_string]
    data = [running_lines, waiting_lines]
    GridPrinter(data, title=title, secitons=sections, headers=headers)

  def _get_columns(self, line: List[str], **kwargs) -> List[str]:
    ret = []
    center = kwargs.get("center", False)
    for i, value in enumerate(line):
      if i in self.columns:
        if center:
          ret.append(value.center(self.spacing - 2))
        else:
          ret.append(f"{value:{self.spacing-2}}")
    return list(
        map(lambda x: x[1],
            sorted((self.colmn_sort[i][1], ret[i]) for i in range(len(ret)))))


class GridPrinter(object):
  def __init__(self, data, **kwargs):
    self.title = kwargs.get("title", None)
    self.sections = kwargs.get("sections", None)
    self.headers = kwargs.get("headers", None)
    self.data = data
    self.corner_icon = kwargs.get("corner_icon", "+")
    self.col_width = kwargs.get("col_width", 10)
    self.col_widths = []
    self.col_seperator_icon = kwargs.get("col_seperator_icon", "|")
    self.col_spacing = kwargs.get("col_spacing", 1)
    self.row_seperator_icon = kwargs.get("row_seperator_icon", "-")
    self.num_columns = len(self.headers[0])
    # headers_dim = self.check_dimensions(headers)
    # headers_dim.insert(1,1)
    # if headers_dim != self.check_dimensions(data):
    #   print(f"""The dimensions for the header and data do not match
    #       (header:{self.check_dimensions(headers)}, data: {self.check_dimensions(data)}""")
    #   exit(1)
    self.update_widths(0)
    self._print_break()
    if self.title:
      self._print_centered_string(self.title)
    for i in range(len(self.data)):
      self.update_widths(i)
      if self.sections:
        self._print_centered_string(self.sections[i])
      if self.headers:
        self._print_header(self.headers[i])
      self._print_data_section(self.data[i])

  def _print_data_section(self, data_section):
    if not len(data_section):
      self._print_centered_string("NO ITEMS", bcolors.FAIL)
      return
    for line in data_section:
      print(self.col_seperator_icon, end="")
      for (index, entry) in enumerate(line):
        print(" " * self.col_spacing, end="")
        print(f"{entry:{self.col_widths[index]}}", end="")
        print(" " * self.col_spacing, end="")
        print(self.col_seperator_icon, end="")
      print()
    self._print_break()

  def _print_break(self):
    print(self.corner_icon + f"{self.row_seperator_icon * (self.full_width)}" +
          self.corner_icon)

  def update_widths(self, index):
    self.col_widths = [len(i) for i in self.headers[index]]
    transpose_data = list(map(list, zip(*self.data[index])))
    for idx in range(len(transpose_data)):
      self.col_widths[idx] = max(max(len(j) for j in transpose_data[idx]),
                                 self.col_widths[idx])

  def _print_header(self, headers):
    print(self.col_seperator_icon, end="")
    for (idx, line) in enumerate(headers):
      print(" " * self.col_spacing, end="")
      print(f"{line:{self.col_widths[idx]}}", end="")
      print(" " * self.col_spacing, end="")
      print(self.col_seperator_icon, end="")
    print()
    self._print_break()

  def _print_centered_string(self, string, color=bcolors.BOLD):
    string = bcolors.color_full_text(color, string.center(self.full_width))
    print(self.col_seperator_icon + string + self.col_seperator_icon)
    self._print_break()

  def check_dimensions(self, arr):
    ret = []
    curr = arr
    while type(curr) is list:
      ret.append(len(curr))
      if len(curr) == 0:
        break
      curr = curr[0]
    return ret

  @property
  def full_width(self):
    return self.num_columns * (
        (self.col_spacing * 2) + len(self.col_seperator_icon)) - 1 + sum(
            self.col_widths)
