class bcolors:
  NORMAL = '\033[0m'
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  ERRORRED = '\033[31m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

  @staticmethod
  def color_full_text(color, string):
    return f"{color}{string}{bcolors.NORMAL}"