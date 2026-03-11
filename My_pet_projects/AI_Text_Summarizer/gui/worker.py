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
            print("DEBUG: Worker started, начинаем стриминг...")
            for tok in self.engine.stream(self.prompt):
                self.token.emit(tok)
            print("DEBUG: Worker finished successfully")
        except Exception as e:
            print(f"DEBUG: Worker error: {e}")
            self.error.emit(str(e))