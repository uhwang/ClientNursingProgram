import sys
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QCursor, QDragEnterEvent, QDropEvent
from pathlib import Path

class DraggablePictureLabel(QLabel):

    set_picture_path = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px dashed #999; background-color: #f0f0f0; color: #666;")
        self.setText("Drag and drop a picture here\n(or use 'Browse')")
        self.setAcceptDrops(True)
        self.picture_path = ""

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
            self.setCursor(QCursor(Qt.PointingHandCursor))
            self.setStyleSheet("border: 2px dashed #333; background-color: #e0e0e0; color: #333;")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.setStyleSheet("border: 2px dashed #999; background-color: #f0f0f0; color: #666;")

    def dropEvent(self, event: QDropEvent):
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.setStyleSheet("border: 2px dashed #999; background-color: #f0f0f0; color: #666;")
        for url in event.mimeData().urls():
            if url.isLocalFile():
                self.set_picture(url.toLocalFile())
                u_ = url.path()
                if u_[0] == '/':
                    u_ = u_[1:]
                self.set_picture_path.emit(u_)
                break
        event.accept()

    def set_picture(self, file_path):
        if file_path:
            self.picture_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.setPixmap(scaled_pixmap)
                self.setText("")
            else:
                self.setPixmap(QPixmap())
                self.setText("Invalid Image")
        else:
            self.setPixmap(QPixmap())
            self.setText("Drag and drop a picture here\n(or use 'Browse')")
            self.picture_path = ""