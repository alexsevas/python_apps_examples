from PyQt5.QtCore import QThread, pyqtSignal

class Worker(QThread):
    """Worker для выполнения генерации в отдельном потоке"""
    
    token = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, engine, prompt):
        super().__init__()
        self.engine = engine
        self.prompt = prompt
        self.should_stop = False

    def run(self):
        """Выполняет генерацию с возможностью остановки"""
        try:
            print("DEBUG: Worker started, начинаем стриминг...")
            for tok in self.engine.stream(self.prompt):
                if self.should_stop:
                    print("DEBUG: Worker stopped by user")
                    break
                self.token.emit(tok)
            print("DEBUG: Worker finished successfully")
        except Exception as e:
            print(f"DEBUG: Worker error: {e}")
            self.error.emit(str(e))
    
    def stop(self):
        """Останавливает генерацию"""
        self.should_stop = True