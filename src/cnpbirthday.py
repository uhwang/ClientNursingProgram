'''
    cnpbirthday.py
'''
from PyQt5.QtWidgets import (
     QWidget      , QPushButton   , QHBoxLayout   , QVBoxLayout, 
     QDialog      , QFormLayout   , QComboBox,
     QStyleFactory, QTableWidget  , QTableWidgetItem, 
     QTableWidgetItem, QGridLayout, QCheckBox, QGridLayout
)

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont

import cnpdb, cnpval, cnpconf, cnpvtbl, msg
import icon_system, icon_view_setting

_all_selected = "All"
_none_selected = "None"

class QSearchBirthdayDlg(QDialog):
    def __init__(self, db_man, all_column, visible_columns, gmsg):
        super(QSearchBirthdayDlg, self).__init__()
        layout = QFormLayout()
        
        self.db_man = db_man
        self.client_list = None
        self.all_column = all_column
        self.visible_columns = visible_columns
        self.gmsg = gmsg
        self.birth_month = []
        m_layout = QGridLayout()
        
        r_, c_ = 2, 6
        for i_ in range(r_):
            for j_ in range(c_):
                w_ = QCheckBox(cnpval.month[i_*c_+j_])
                self.birth_month.append(w_)
                m_layout.addWidget(w_,i_,j_)
        
        self.all_btn = QPushButton(_none_selected)
        self.all_btn.setCheckable(True)
        
        # Use a style sheet for a more advanced look
        self.all_btn.setStyleSheet("""
            /* Default state (unchecked) */
            QPushButton {
                background-color: #e0e0e0;
                border: 3px solid #a0a0a0;
                border-radius: 3px;
                padding: 0px 0px;
                font-size: 12px;
                color: #333;
                qproperty-icon: url(icon_okbtn.png); /* You can add an icon here */
            }
            
            /* Hover state */
            QPushButton:hover {
                background-color: #d0d0d0;
                border-color: #808080;
            }
            
            /* Pressed state (before toggling) */
            QPushButton:pressed {
                background-color: #c0c0c0;
                border-style: inset;
                border-color: #707070;
            }
    
            /* Checked state (toggled on) */
            QPushButton:checked {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4CAF50, stop: 1 #45a049);
                color: white;
                border: 2px solid #388E3C;
                border-style: outset;
            }
            
            /* Hover state when checked */
            QPushButton:checked:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #45a049, stop: 1 #388E3C);
            }
            """)

        self.ok = QPushButton('OK')
        self.cancel = QPushButton('CANCEL')
        
        self.all_btn.clicked.connect(self.on_button_toggled)
        self.ok.clicked.connect(self.search_client_birthday)
        self.cancel.clicked.connect(self.reject)
        
        self.column_setting = QPushButton()
        self.column_setting.setIcon(QIcon(QPixmap(icon_view_setting.table)))
        self.column_setting.setIconSize(QSize(16,16))
        self.column_setting.clicked.connect(self.change_view_setting)
        self.column_setting.setToolTip('Customize columns')

        i_ += 1
        m_layout.addWidget(self.all_btn, i_, 0)
        m_layout.addWidget(self.ok, i_, 1)
        m_layout.addWidget(self.cancel, i_, 2)
        m_layout.addWidget(self.column_setting, i_, 3)

        header_ = cnpconf.get_birtday_columns()
        self.view_table = QTableWidget()
        self.view_table.setColumnCount(len(header_))
        self.view_table.setHorizontalHeaderLabels(header_)
        self.view_table.horizontalHeader().setStretchLastSection(True) 

        i_ += 1
        m_layout.addWidget(self.view_table, i_, 0, 1, 6)

        self.setLayout(m_layout)
        self.setWindowTitle("Find Birthday")
        self.setWindowIcon(QIcon(QPixmap(icon_system.table)))

    def set_month_status(self, status = False):
        for m_ in self.birth_month:
            m_.setChecked(status)
            
    # Connect a function to change the text based on the state
    def on_button_toggled(self, checked):
        if checked:
            self.all_btn.setText(_all_selected)
            self.set_month_status(True)
        else:
            self.all_btn.setText(_none_selected)
            self.set_month_status(False)
        
    def get_month(self):
        return [ m_.text() for m_ in self.birth_month ]
        
    def change_view_setting(self):
        # view_table, all_columns, visible_columns, update_visible_column, gmsg):
        cnpvtbl.show_customize_dialog(self.client_list,
                                      self.view_table, 
                                      self.all_column, 
                                      self.visible_columns,
                                      cnpconf.update_birthday_column,
                                      self.gmsg)
    def search_client_birthday(self):
        if not any([m_.isChecked() for m_ in self.birth_month]):
            msg.message_box("Select at least any month")
            return 
            
        key = [f"{cnpdb.available_view_column_key(v_)}" for v_ in self.visible_columns]
        v_key = ','.join(key)
        
        try:
            if self.all_btn.text() == _all_selected:
                query = f"SELECT {v_key} FROM {cnpdb.table_name} ORDER BY dob ASC"
                self.client_list = self.db_man.db.execute_query(query, key)
            else:
                # create a query
                m_idx = [cnpval.month_index[m_.text()] for m_ in self.birth_month if m_.isChecked()]
                m_str = ', '.join([f"'{m_}'" for m_ in m_idx])
                query = f"SELECT {v_key} FROM {cnpdb.table_name} WHERE SUBSTR({cnpdb.col_dob}, 1, 2) IN ({m_str}) ORDER BY dob ASC"
                self.client_list = self.db_man.db.execute_query(query, key)
        except Exception as e:
            e_msg = f"Error: {e}"
            self.gmsg.appendPlainText(e_msg)
            msg.message_box(e_msg)
            return
            
        if self.client_list == []:
            msg.message_box("No client exist")
            return 

        cnpvtbl.update_view_table(self.client_list, self.view_table, self.visible_columns)
            
def search_birthday(db_man, gmsg):
    all_columns = [c for c in cnpdb.view_table_head_label]
    visible_columns = cnpconf.get_birtday_columns()
    
    b_ = QSearchBirthdayDlg(db_man, all_columns, visible_columns, gmsg)
    ret = b_.exec_()
    if ret == QDialog.Accepted:
        m_ = b_.get_month()
        print(b_)
        return
        v_key = cnpconf.get_birthday_column()        
        
        try:
            db_man.db.custom_query(v_key)
        except Exception as e:
            e_msg = f"... Error:{e}"
            msg.message_box(e_msg)
            self.global_message.appendPlainText(e_msg)
            return
            
        # multi column sort by month in case of all months
        
        # just return the list of clients in case of 
            
        
