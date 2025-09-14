'''
    cnpfind.py : CNP Find client
'''
from PyQt5.QtWidgets import (
     QWidget    , QLabel        , QLineEdit, 
     QPushButton, QHBoxLayout   , QVBoxLayout, 
     QComboBox  , QDialog       , QGridLayout, 
     QTableWidget, QTableWidgetItem
     )
     
from PyQt5.QtGui import QPixmap, QIcon     
import msg
import icon_system
_search_by_lname_kr = 0
_search_by_fname_kr = 1
_search_by_lname_en = 2
_search_by_fname_en = 3
        
class FindDialog(QDialog):
    def __init__(self, db, view=False):
        super().__init__()
        self.db = db
        self.result = None
        self.view = view
        self.setWindowTitle("Find Client")
        layout = QVBoxLayout()

        self.search_field = QComboBox()
        self.search_field.addItems([
            "last_name_kr", "first_name_kr",
            "last_name_en", "first_name_en",
            #"dob", "room_number"
        ])
        self.search_field.setCurrentIndex(_search_by_fname_en)
        
        l_ = QGridLayout()
        self.search_value = QLineEdit()
        self.find_button = QPushButton("Find")
        self.find_button.clicked.connect(self.search)

        l_.addWidget(QLabel("Search by:"),0,0)
        l_.addWidget(self.search_field,0,1)
        l_.addWidget(QLabel("Value:"),1,0)
        l_.addWidget(self.search_value,1,1)
        l_.addWidget(self.find_button,2,0,1,2)
        layout.addLayout(l_)
        
        if not view:
            self.client_table = QTableWidget()
            header_ = ["Last", "First"]
            self.client_table.setColumnCount(len(header_))
            self.client_table.setHorizontalHeaderLabels(header_)
            self.client_table.horizontalHeader().setStretchLastSection(True) 
            layout.addWidget(self.client_table)
        
        l_ = QHBoxLayout()
        self.ok = QPushButton('OK')
        self.ok.clicked.connect(self.accept)
        self.cancel = QPushButton('CANCEL')
        self.cancel.clicked.connect(self.reject)
        l_.addWidget(self.ok)
        l_.addWidget(self.cancel)
        layout.addLayout(l_)
        
        self.setLayout(layout)
        self.setWindowTitle("Find a client")
        self.setWindowIcon(QIcon(QPixmap(icon_system.table)))

    def search(self):
        self.field = self.search_field.currentIndex()
        value = self.search_value.text().strip()
        
        if value == "":
            msg.message_box("No name!!", msg.message_warning)
            return
            
        if self.field == _search_by_lname_kr:
            self.result = self.db.search_by_lastname_kr(value)
        elif self.field == _search_by_fname_kr:
            self.result = self.db.search_by_firstname_kr(value)
        elif self.field == _search_by_lname_en:
            self.result = self.db.search_by_lastname_eng(value)
        elif self.field == _search_by_fname_en:
            self.result = self.db.search_by_firstname_eng(value)
            
        if self.result == []:
            msg.message_box("No matching clients found.")
        elif self.view: 
            self.accept()
        else:
            #msg.message_box("%d clients found!"%len(self.result))
            
            self.client_table.setRowCount(len(self.result))
            for row_idx, row_data in enumerate(self.result):
                if self.field == _search_by_lname_kr or \
                   self.field == _search_by_fname_kr:
                    l_name = row_data[cnpdb.col_last_name_kor]
                    f_name = row_data[cnpdb.col_first_name_kor]
                elif self.field == _search_by_lname_en or \
                   self.field == _search_by_fname_en:
                    l_name = row_data[cnpdb.col_last_name_eng]
                    f_name = row_data[cnpdb.col_first_name_eng]
                
                self.client_table.setItem(row_idx, 0, QTableWidgetItem(l_name)) 
                self.client_table.setItem(row_idx, 1, QTableWidgetItem(f_name)) 
                
    def selected_client(self):
        if not self.view:
            r_ = self.client_table.currentRow()
            if r_ >= 0:
                return self.result[r_]
            else:
                return None
            
            
    def get_clients(self):
        return self.result

