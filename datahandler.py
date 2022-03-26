class Date:
  def __init__(self, day=1, month=1, year=1984):
    self.day = day
    self.month = month
    self.year = year

class Film:
  def __init__(self, data_string):
    data = data_string.split(",")
    self.name = data[0]
    self.genre = data[1]
    self.link = data[2]

  def to_json(self):
    return f"{self.name}"
