from PyQt5.QtWidgets import (
    QComboBox,
    QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal

class PopupCombo(QFrame):

    set_current_item = pyqtSignal(str)

    def __init__(self, parent=None, items=[]):
        super().__init__(parent, flags=Qt.Popup)  # Popup style makes it disappear on outside click
        self.combo = QComboBox(self)
        #self.combo.addItems(["Option 1", "Option 2", "Option 3"])
        self.combo.addItems(items)
        self.combo.setFocusPolicy(Qt.StrongFocus)
        self.combo.activated.connect(self.close)  # close when selecting
        self.combo.installEventFilter(self)
        
        # Connect the combo's activated signal to our new method
        self.combo.activated.connect(self.emit_selected)
        
        # resize frame to fit combo
        self.resize(self.combo.sizeHint())
        
    def emit_selected(self, index):
        """Emits the custom 'selected' signal with the chosen item's text."""
        item_text = self.combo.currentText()
        self.set_current_item.emit(item_text)
        self.close()
        
    def eventFilter(self, obj, event):
        if obj == self.combo and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.close()
                return True
        return super().eventFilter(obj, event)