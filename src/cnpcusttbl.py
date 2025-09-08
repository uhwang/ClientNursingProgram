from PyQt5.QtWidgets import (
     QLabel  , QPushButton      , QHBoxLayout   , QVBoxLayout, 
     QDialog , QAbstractItemView, QListWidget   , QDialogButtonBox
               , 
)
from PyQt5.QtCore import Qt, QDate, QSize, QObject, pyqtSignal, QPoint
from PyQt5.QtGui import QPixmap, QIcon, QFont

import icon_up, icon_down, icon_system

class CustomizeTableDlg(QDialog):
    def __init__(self, available_columns, selected_columns, parent=None):
        super(CustomizeTableDlg, self).__init__(parent)
        self.setWindowTitle("Customize Table Columns")
        
        self.available_columns = available_columns
        self.selected_columns = selected_columns
        self.initUI()
        self.setWindowTitle("Add or Remove Columns")
        self.setWindowIcon(QIcon(QPixmap(icon_system.table)))
        
    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Left ListWidget (Available Columns)
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Available Columns"))
        self.available_list = QListWidget()
        self.available_list.addItems(self.available_columns)
        self.available_list.setSelectionMode(QAbstractItemView.SingleSelection)
        left_layout.addWidget(self.available_list)
        
        # Center Buttons (Add/Remove)
        button_layout = QVBoxLayout()
        add_btn = QPushButton("--> Add")
        remove_btn = QPushButton("<-- Remove")
        button_layout.addStretch()
        button_layout.addWidget(add_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addStretch()
        
        # Right ListWidget (Selected Columns) and Reorder Buttons
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Selected Columns"))
        
        right_list_layout = QHBoxLayout()
        self.selected_list = QListWidget()
        self.selected_list.addItems(self.selected_columns)
        self.selected_list.setSelectionMode(QAbstractItemView.SingleSelection)
        
        reorder_button_layout = QVBoxLayout()
        move_up_btn = QPushButton()
        move_up_btn.setIcon(QIcon(QPixmap(icon_up.table)))
        move_up_btn.setIconSize(QSize(32,32))
        
        move_down_btn = QPushButton()
        move_down_btn.setIcon(QIcon(QPixmap(icon_down.table)))
        move_down_btn.setIconSize(QSize(32,32))
        
        reorder_button_layout.addStretch()
        reorder_button_layout.addWidget(move_up_btn)
        reorder_button_layout.addWidget(move_down_btn)
        reorder_button_layout.addStretch()
        
        right_list_layout.addWidget(self.selected_list)
        right_list_layout.addLayout(reorder_button_layout)
        
        right_layout.addLayout(right_list_layout)
        
        # Dialog buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        # Connect button signals to methods
        add_btn.clicked.connect(self.add_item)
        remove_btn.clicked.connect(self.remove_item)
        move_up_btn.clicked.connect(self.move_up)
        move_down_btn.clicked.connect(self.move_down)
        
        # Final Layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(right_layout)
        
        final_layout = QVBoxLayout()
        final_layout.addLayout(main_layout)
        final_layout.addWidget(self.buttonBox)
        self.setLayout(final_layout)
        
    def add_item(self):
        current_item = self.available_list.currentItem()
        if current_item:
            row = self.available_list.row(current_item)
            item_text = self.available_list.takeItem(row)
            self.selected_list.addItem(item_text)
            self.selected_list.setCurrentItem(self.selected_list.item(self.selected_list.count() - 1))

    def remove_item(self):
        current_item = self.selected_list.currentItem()
        if current_item:
            row = self.selected_list.row(current_item)
            item_text = self.selected_list.takeItem(row)
            self.available_list.addItem(item_text)
            
    def move_up(self):
        current_item = self.selected_list.currentItem()
        if current_item:
            row = self.selected_list.row(current_item)
            if row > 0:
                item = self.selected_list.takeItem(row)
                self.selected_list.insertItem(row - 1, item)
                self.selected_list.setCurrentRow(row - 1)
                
    def move_down(self):
        current_item = self.selected_list.currentItem()
        if current_item:
            row = self.selected_list.row(current_item)
            if row < self.selected_list.count() - 1:
                item = self.selected_list.takeItem(row)
                self.selected_list.insertItem(row + 1, item)
                self.selected_list.setCurrentRow(row + 1)
            
    def get_selected_columns(self):
        return [self.selected_list.item(i).text() for i in range(self.selected_list.count())]
        