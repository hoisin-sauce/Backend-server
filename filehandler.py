import glob

class File:
  def __init__(self, filename):
    self.filename = filename

    # check if file exists
    if not filename in glob.glob("*"):
      self.clear_file()

  def clear_file(self):
    open(self.filename, "w").close()

  def append(self, data):
    with open(self.filename, "a") as file:
      file.write(f"\n{data}")

  def append_bytes(self, data):
    with open(self.filename, "ab") as file:
      file.write(data + b"\n")

  def get_data(self):
    with open(self.filename, "r") as file:
      data = file.readlines()
    return data

  def get_data_bytes(self):
    with open(self.filename, "rb") as file:
      data = file.readlines()
    return data

  def replace_line(self, line_num, text, newl=True):
    with open(self.filename, 'r') as file:
      lines = file.readlines()
      lines[line_num] = text + "\n" if  line_num + 1 < self.len and newl else text
      with open(self.filename, 'w') as out:
        out.writelines(lines)

  def replace_line_bytes(self, line_num, text):
    with open(self.filename, 'rb') as file:
      lines = file.readlines()
      lines[line_num] = text if line_num + 1 < self.len else text +  b"\n"
      with open(self.filename, 'wb') as out:
        out.writelines(lines)

  @property
  def len(self):
    try:
      return len(self.get_data())
    except UnicodeDecodeError:
      return len(self.get_data_bytes())

  def __enter__(self):
    return self