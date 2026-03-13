import fitz
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPixmap


class PDFViewer(QGraphicsView):

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.zoom = 1.0
        self.current_doc = None

    def load_pdf(self, path):
        """Загружает PDF файл с обработкой ошибок"""
        try:
            # Закрываем предыдущий документ если есть
            if self.current_doc:
                self.current_doc.close()
                self.current_doc = None
            
            self.scene.clear()
            self.current_doc = fitz.open(path)
            y = 0
            
            for page in self.current_doc:
                pix = page.get_pixmap()
                img = QPixmap()
                if not img.loadFromData(pix.tobytes()):
                    raise Exception(f"Failed to load page {page.number}")
                item = self.scene.addPixmap(img)
                item.setOffset(0, y)
                y += img.height()
                
        except Exception as e:
            if self.current_doc:
                self.current_doc.close()
                self.current_doc = None
            raise Exception(f"Failed to load PDF: {str(e)}")

    def clear(self):
        """Очищает viewer и освобождает ресурсы"""
        if self.current_doc:
            self.current_doc.close()
            self.current_doc = None
        self.scene.clear()
        self.zoom = 1.0
        self.resetTransform()

    def wheelEvent(self, event):
        """Обработка зума колесиком мыши"""
        if event.angleDelta().y() > 0:
            self.zoom *= 1.2
        else:
            self.zoom /= 1.2
        
        # Ограничиваем зум
        self.zoom = max(0.1, min(self.zoom, 10.0))
        
        self.resetTransform()
        self.scale(self.zoom, self.zoom)
    
    def closeEvent(self, event):
        """Очистка при закрытии"""
        self.clear()
        super().closeEvent(event)