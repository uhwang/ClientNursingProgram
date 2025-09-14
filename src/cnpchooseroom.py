class QChooseRoomNumberDlg(QDialog):
    def __init__(self, db):
        super(QChooseRoomNumberDlg, self).__init__()
        self.db = db
        self.initUI()
        self.room_number_tbl.resizeColumnsToContents()
        self.setWindowTitle("Find a room")
        self.setWindowIcon(QIcon(QPixmap(icon_system.table)))

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Table setup
        self.room_number_tbl = QTableWidget()
        self.room_number_tbl.setColumnCount(1)
        self.room_number_tbl.setHorizontalHeaderItem(0, QTableWidgetItem("Room#"))
        
        # This line makes the single column stretch to fill the available width
        self.room_number_tbl.horizontalHeader().setStretchLastSection(True) 
        
        # Disable horizontal scroll bar
        self.room_number_tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        rm = self.db.get_rooms()
        
        # Add rows before setting items
        self.room_number_tbl.setRowCount(len(rm))
        
        for k, r in enumerate(rm):
            item = QTableWidgetItem(r)
            self.room_number_tbl.setItem(k, 0, item)
        
        self.room_number_tbl.resizeColumnsToContents()
        
        # Grid layout for controls
        control_layout = QGridLayout()
        
        self.ok = QPushButton('OK')
        self.cancel = QPushButton('CANCEL')
        self.ok.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.reject)
        
        control_layout.addWidget(self.ok, 1, 0)
        control_layout.addWidget(self.cancel, 1, 1)
        
        # Add widgets to the main layout
        main_layout.addWidget(self.room_number_tbl)
        main_layout.addLayout(control_layout)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Choose Room#")
        
    def get_current_room(self):
        return self.room_number_tbl.currentRow()
