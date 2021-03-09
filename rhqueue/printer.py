from typing import List
from rhprinter import bcolors
from itertools import zip_longest


class GridPrinter(object):
    def __init__(self, data, **kwargs):
        self.title = kwargs.get("title", None)
        self.sections = kwargs.get("sections", None)
        self.headers = kwargs.get("headers", None)
        self.data = data
        self.corner_icon = kwargs.get("corner_icon", "+")
        self.col_width = kwargs.get("col_width", -1)
        self.col_widths = []
        self.col_seperator_icon = kwargs.get("col_seperator_icon", "|")
        self.col_spacing = kwargs.get("col_spacing", 1)
        self.row_seperator_icon = kwargs.get("row_seperator_icon", "-")
        self.num_columns = len(self.headers[0])
        self.col_widths = self.update_widths(self.headers + self.data)
        self._print_break()
        if self.title:
            self._print_centered_string(self.title)
        for i in range(len(self.data)):
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
        print(self.corner_icon +
              f"{self.row_seperator_icon * (self.full_width)}" +
              self.corner_icon)

    def update_widths(self, lst) -> List[int]:
        if isinstance(lst, list) and all(isinstance(i, str) for i in lst):
            return [len(i) for i in lst]
        val = []
        for i in lst:
            val.append(self.update_widths(i))
        if len(val) < 2:
            val.append([])
        val = list(zip_longest(*val, fillvalue=0))
        return [max(*i) for i in val]

    def _print_header(self, headers):
        print(self.col_seperator_icon, end="")
        for (idx, line) in enumerate(headers):
            print(" " * self.col_spacing, end="")
            print(f"{line.center(self.col_widths[idx])}", end="")
            print(" " * self.col_spacing, end="")
            print(self.col_seperator_icon, end="")
        print()
        self._print_break()

    def _print_centered_string(self, string, color=bcolors.BOLD):
        string = bcolors.color_full_text(color, string.center(self.full_width))
        print(self.col_seperator_icon + string + self.col_seperator_icon)
        self._print_break()

    @property
    def full_width(self):
        return self.num_columns * (
            (self.col_spacing * 2) + len(self.col_seperator_icon)) - 1 + sum(
                self.col_widths)
