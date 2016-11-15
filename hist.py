class FileHistory():
    hist = [""]

    @staticmethod
    def add_entry(path, type):
        FileHistory.hist.push((path, type))

    @staticmethod
    def get_entry_pointer():
        return FileHistoryPointer(len(FileHistory.hist) - 1)


class FileHistoryPointer():

    def __init__(self, i):
        self.i = i

    def up(self):
        if self.i > 0:
            self.i -= 1
        return FileHistory.hist[self.i]

    def down(self):
        if self.i < len(FileHistory.hist[self.i]):
            self.i += 1
        return FileHistory.hist[self.i]
