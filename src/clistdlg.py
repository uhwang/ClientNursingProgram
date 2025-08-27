from PyQt5.QtWidgets import (
     QWidget      , QPushButton   , QHBoxLayout   , QVBoxLayout, 
     QDialog      , QFormLayout   , 
     QStyleFactory, QTableWidget  , QTableWidgetItem, 
     QTableWidgetItem, 
)

from PyQt5.QtCore import Qt

import cnpdb

class QClientListDlg(QDialog):
    def __init__(self, c_list):
        super(QClientListDlg, self).__init__()
        self.c_list = c_list
        self.initUI()
        self.client_tbl.resizeColumnsToContents()

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Table setup
        self.client_tbl = QTableWidget()
        self.client_tbl.setColumnCount(3)
        self.client_tbl.setHorizontalHeaderItem(0, QTableWidgetItem("Room#"))
        self.client_tbl.setHorizontalHeaderItem(1, QTableWidgetItem("Fist"))
        self.client_tbl.setHorizontalHeaderItem(2, QTableWidgetItem("Last"))
        
        # This line makes the single column stretch to fill the available width
        self.client_tbl.horizontalHeader().setStretchLastSection(True) 
        
        # Disable horizontal scroll bar
        self.client_tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Add rows before setting items
        self.client_tbl.setRowCount(len(self.c_list))
        
        for k, c in enumerate(self.c_list):
            print(c)
            f_ = QTableWidgetItem(c[cnpdb.col_first_name_kor])
            l_ = QTableWidgetItem(c[cnpdb.col_last_name_kor])
            r_ = QTableWidgetItem(c[cnpdb.col_room_number])
            self.client_tbl.setItem(k, 0, f_)
            self.client_tbl.setItem(k, 1, l_)
            self.client_tbl.setItem(k, 2, r_)
        
        self.client_tbl.resizeColumnsToContents()
        
        # Grid layout for controls
        control_layout = QHBoxLayout()
        
        self.ok = QPushButton('OK')
        self.cancel = QPushButton('CANCEL')
        self.ok.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.reject)
        
        control_layout.addWidget(self.ok)
        control_layout.addWidget(self.cancel)
        
        # Add widgets to the main layout
        main_layout.addWidget(self.client_tbl)
        main_layout.addLayout(control_layout)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Client List")
        