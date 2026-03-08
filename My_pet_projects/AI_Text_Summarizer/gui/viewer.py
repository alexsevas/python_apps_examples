import fitz
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPixmap


class PDFViewer(QGraphicsView):

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.zoom = 1.0

    def load_pdf(self, path):
        self.scene.clear()
        doc = fitz.open(path)
        y = 0
        for page in doc:
            pix = page.get_pixmap()
            img = QPixmap()
            img.loadFromData(pix.tobytes())
            item = self.scene.addPixmap(img)
            item.setOffset(0, y)
            y += img.height()


    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom *= 1.2
        else:
            self.zoom /= 1.2
        self.resetTransform()
        self.scale(self.zoom, self.zoom)