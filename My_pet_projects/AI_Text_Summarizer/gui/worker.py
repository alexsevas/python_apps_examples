from PyQt5.QtCore import QThread, pyqtSignal

class Worker(QThread):

    token = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, engine, prompt):
        super().__init__()
        self.engine = engine
        self.prompt = prompt


    def run(self):
        try:
            for tok in self.engine.stream(self.prompt):
                self.token.emit(tok)
        except Exception as e:
            self.error.emit(str(e))