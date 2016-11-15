class FileHistory():
    hist = []

    @staticmethod
    def add_entry(path):
        FileHistory.hist.append(path)

    @staticmethod
    def get_history():
        return FileHistoryOb(FileHistory.hist[0:])


class FileHistoryOb():

    def __init__(self, hist):
        self.hist = hist
        self.hist.append("")
        self.i = len(self.hist) - 1

    def up(self):
        print(self.hist)
        if self.i > 0:
            self.i -= 1
        return self.hist[self.i]

    def down(self):
        print(self.i)
        if self.i < len(self.hist[self.i]):
            self.i += 1
        return self.hist[self.i]

    def update(self, path):
        self.hist[self.i] = path
