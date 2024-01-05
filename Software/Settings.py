from datetime import timedelta
import json

class Settings:
    def __init__(self):
        self.__study_time = timedelta(minutes=25)
        self.__short_break_length = timedelta(minutes=5)
        self.__long_break_length = timedelta(minutes=30)
        self.__long_break_intervals = 4

    @property
    def study_time(self):
        return self.__study_time

    @study_time.setter
    def study_time(self, value):
        if isinstance(value, timedelta):
            self.__study_time = value

    @property
    def short_break_length(self):
        return self.__short_break_length

    @short_break_length.setter
    def short_break_length(self, value):
        if isinstance(value, timedelta):
            self.__short_break_length = value

    @property
    def long_break_length(self):
        return self.__long_break_length

    @long_break_length.setter
    def long_break_length(self, value):
        if isinstance(value, timedelta):
            self.__long_break_length = value

    @property
    def long_break_intervals(self):
        return self.__long_break_intervals

    @long_break_intervals.setter
    def long_break_intervals(self, value):
        if isinstance(value, int):
            self.__long_break_intervals = value

    def save_to_file(self, filename):
        with open(filename, "w") as file:
            json.dump({
                "study_time": self.study_time.seconds,
                "short_break_length": self.short_break_length.seconds,
                "long_break_length": self.long_break_length.seconds,
                "long_break_intervals": self.long_break_intervals
            }, file)

    def load_from_file(self, filename):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                self.study_time = timedelta(seconds=data["study_time"])
                self.short_break_length = timedelta(seconds=data["short_break_length"])
                self.long_break_length = timedelta(seconds=data["long_break_length"])
                self.long_break_intervals = data["long_break_intervals"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
