'''
Creator    : Uisang Hwang
Co-creator : ChatGPT, Gemini

08/24/2025 ... Ver 0.1
08/27/2025 ... Ver 0.2
09/01/2025 ... Ver 0.3
09/13/2025 ... Ver 0.4 

pyinstaller --onefile --windowed --icon=cnp.ico --exclude-module PySide6 --exclude-module tkinter --exclude-module scipy --exclude-module numpy --exclude-module distutils cnp.py
'''

import sys, os, re
from functools import partial
import sqlite3, shutil
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
     QApplication    , QWidget          , QLabel        , QLineEdit, 
     QTextEdit       , QPushButton      , QHBoxLayout   , QVBoxLayout, 
     QFileDialog     , QDateEdit        , QMessageBox   , QComboBox, 
     QDialog         , QFormLayout      , QGroupBox     , QGridLayout, 
     QStyleFactory   , QTabWidget       , QTableWidget  , QTableWidgetItem, 
     QCheckBox       , QCalendarWidget  , QPlainTextEdit, QTableWidget, 
     QTableWidgetItem, QAbstractItemView, QListWidget   , QDialogButtonBox,
     QFrame          , QSizeGrip
)
from PyQt5.QtCore import Qt, QDate, QSize, QObject, pyqtSignal, QPoint
from PyQt5.QtGui import QPixmap, QIcon, QFont

import icon_arrow_left  , icon_arrow_right , icon_folder_open, \
       icon_word        , icon_excel       , icon_document, \
       icon_add         , icon_delete      , icon_update, \
       icon_save        , icon_trash       , icon_house, \
       icon_fetch_all   , icon_save_01     , icon_view_setting, \
       icon_up          , icon_down        , icon_find, \
       icon_num_black_02, icon_num_black_03, icon_num_black_04, \
       icon_num_blue_02 , icon_num_blue_03 , icon_num_blue_04, \
       icon_pdf         , icon_trash_03    , icon_system, \
       icon_note        , icon_id          , icon_logout, \
       icon_clear       , icon_arrow_LR    , icon_birthday, \
       icon_chart 

import cnpdb, cidman, msg, cnpval, clistdlg, cnppdf, cnpconf, \
       cnpword, cnpexcel, cnputil, cnpconf, cnpdrag, cnpcomb, \
       cnpccoord, cnpfind, cnpvtbl
       
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eben Silver Town Client Nursing Program")
        
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.message_tab(), "Message")
        cnpconf.load_config(self.global_message)

        self.tabs.addTab(self.build_entry_tab(), "Add/Edit Client")
        self.tabs.addTab(self.build_view_tab(), "View/Search Clients")
        #self.tabs.addTab(self.config_tab(), "Config")
        
        self.tabs.tabBar().moveTab(0,2)
        self.tabs.setCurrentIndex(0)
        layout.addWidget(self.tabs)
        self.setLayout(layout)   

        self.db_man = cnpccoord.ClientCoordinator()
        self.db_man.print_message.connect(self.print_concurrent_message)
        self.db_man.db.print_message.connect(self.print_concurrent_message)
        
        if not self.db_man.db.check():
            msg.message_box("... Error : invalid db. See messages.", msg.message_error)
        else:
            self.global_message.appendPlainText("... Load All clients")
            self.db_man.load()
            self.global_message.appendPlainText(f"... {self.db_man.count()} clients loaded")
            
        self.setWindowIcon(QIcon(QPixmap(icon_system.table)))
        
    def config_tab(self):
        pass
        
    def closeEvent(self, event):
        ret = msg.message_box("Are you sure you want to quit?", msg.message_yesno)
        if ret == QMessageBox.Yes: 
            self.db_man.close()
            cnpconf.save_config(self.global_message)
            event.accept()
        else:
            event.ignore()
            
    def show_current_client(self, selected_client=None):
        #self.global_message.appendPlainText("... show_current_client")
        if selected_client is None:
            client = self.db_man.current_client()
        else:
            client = selected_client
            
        if client is None:
            msg.message_box("... Warning: no client data.")
            return
        
        pic_path = client[cnpdb.col_pic_path]
        
        if pic_path is not None and Path(pic_path).exists() == True:
            self.file_path.setText(pic_path)
            pixmap = QPixmap(pic_path).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.picture_label.setPixmap(pixmap)
            
        client_id = client[cnpdb.col_id]
        self.name_box.setTitle(f"Names: ID({client_id})")
        
        pic_path = cnputil.safe_val(client[cnpdb.col_pic_path])
        self.file_path.setText(pic_path)  

        if pic_path != "" and Path(pic_path).exists() == True:
            pixmap = QPixmap(pic_path).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.picture_label.setPixmap(pixmap)
        
        self.first_name_kr .setText(client[cnpdb.col_first_name_kor ])   
        self.last_name_kr  .setText(client[cnpdb.col_last_name_kor  ])   
        self.first_name_en .setText(client[cnpdb.col_first_name_eng ])   
        self.middle_name_en.setText(client[cnpdb.col_middle_name_eng])   
        self.last_name_en  .setText(client[cnpdb.col_last_name_eng  ])  

        d_ = client[cnpdb.col_dob][0:10] # get only MM/dd/yyyy
        new_date = QDate.fromString(d_, cnpval.date_format_w)
        self.dob.setDate(new_date)
        self.calculate_age()
        
        s_ = client[cnpdb.col_sex]
        self.sex.setCurrentIndex(0 if s_ == 'M' else 1)
        
        self.room_number       .setText(client[cnpdb.col_room_number])
        self.initial_assessment.setText(client[cnpdb.col_initial_assessment])
        self.assessment_14th   .setText(client[cnpdb.col_assessment_14th])
        self.assessment_90th   .setText(client[cnpdb.col_assessment_90th])
        self.change_assessment .setText(client[cnpdb.col_change_assessment])
        s_ = client[cnpdb.col_change_assessment_done]
        self.change_assessment_check.setChecked(True if s_ == cnpdb.change_assessment_yes else False)
        
        self.comments.setPlainText(client[cnpdb.col_comments])
        
    def print_concurrent_message(self, msg):
        self.global_message.appendPlainText(msg)
    
    def message_tab(self):
        widget = QWidget()
        
        layout = QVBoxLayout()
        l_ = QHBoxLayout()
        clear_btn = QPushButton()
        clear_btn.setIcon(QIcon(QPixmap(icon_trash.table)))
        clear_btn.setIconSize(QSize(32,32))
        clear_btn.clicked.connect(self.clear_global_message)
        
        print_id_btn = QPushButton()
        print_id_btn.setIcon(QIcon(QPixmap(icon_id.table)))
        print_id_btn.setIconSize(QSize(32,32))
        print_id_btn.clicked.connect(self.print_id)
        
        l_.addWidget(clear_btn)
        l_.addWidget(print_id_btn)
  
        self.global_message = QPlainTextEdit()
        self.global_message.setFont(QFont("Courier",9,True))
        policy = self.sizePolicy()
        policy.setVerticalStretch(1)
        self.global_message.setSizePolicy(policy)
        self.global_message.setFont(QFont( "Courier,15,-1,2,50,0,0,0,1,0"))

        layout.addWidget(self.global_message)
        layout.addLayout(l_)
        
        widget.setLayout(layout)
        self.global_message.appendPlainText("... Message Tab UI Created")
        return widget

    def print_id(self):
        self.global_message.appendPlainText(f"{self.db_man.cim}")

    def clear_global_message(self):
        self.global_message.clear()
        
    def build_view_tab(self):
        self.global_message.appendPlainText("... Build View Tab")
        widget = QWidget()
        layout = QGridLayout()
        self.view_list = None
        self.all_columns = [c for c in cnpdb.view_table_head_label]
        self.visible_columns = cnpconf.get_visible_columns()
        
        self.view_all = QPushButton()
        self.view_all.setIcon(QIcon(QPixmap(icon_fetch_all.table)))
        self.view_all.setIconSize(QSize(32,32))
        self.view_all.setToolTip('Load all clients from database')
        self.view_all.clicked.connect(self.view_all_client)
        layout.addWidget(self.view_all, 0, 0)

        self.view_search = QPushButton()
        self.view_search.setIcon(QIcon(QPixmap(icon_find.table)))
        self.view_search.setIconSize(QSize(32,32))
        self.view_search.clicked.connect(self.view_search_client)
        self.view_search.setToolTip('Search clients')
        layout.addWidget(self.view_search, 0, 1)

        self.view_save_pdf = QPushButton()
        self.view_save_pdf.setIcon(QIcon(QPixmap(icon_pdf.table)))
        self.view_save_pdf.setIconSize(QSize(32,32))
        self.view_save_pdf.clicked.connect(self.view_saveas_pdf)
        self.view_save_pdf.setToolTip('Save the current list as PDF')
        layout.addWidget(self.view_save_pdf, 0, 2)

        self.view_save_excel = QPushButton()
        self.view_save_excel.setIcon(QIcon(QPixmap(icon_excel.table)))
        self.view_save_excel.setIconSize(QSize(32,32))
        self.view_save_excel.clicked.connect(self.view_saveas_excel)
        self.view_save_excel.setToolTip('Save the current list as Excel')
        layout.addWidget(self.view_save_excel, 0, 3)

        self.view_delete_btn = QPushButton()
        self.view_delete_btn.setIcon(QIcon(QPixmap(icon_delete.table)))
        self.view_delete_btn.setIconSize(QSize(32,32))
        self.view_delete_btn.clicked.connect(self.view_delete)
        self.view_delete_btn.setToolTip('Delete selected client from the list')
        layout.addWidget(self.view_delete_btn, 0, 4)
        
        self.view_clear = QPushButton()
        self.view_clear.setIcon(QIcon(QPixmap(icon_trash.table)))
        self.view_clear.setIconSize(QSize(32,32))
        self.view_clear.clicked.connect(self.view_clear_table)
        self.view_clear.setToolTip('Delete list')
        layout.addWidget(self.view_clear, 0, 5)
 
        self.view_setting = QPushButton()
        self.view_setting.setIcon(QIcon(QPixmap(icon_view_setting.table)))
        self.view_setting.setIconSize(QSize(32,32))
        self.view_setting.clicked.connect(self.change_view_setting)
        layout.addWidget(self.view_setting, 0, 6)

        self.view_table = QTableWidget()
        self.view_table.setColumnCount(len(self.visible_columns))
        self.view_table.setHorizontalHeaderLabels(self.visible_columns)
        self.view_table.setSortingEnabled(True)
        #self.update_view_table()
        cnpvtbl.update_view_table(self.view_list, self.view_table, self.visible_columns)
        
        layout.addWidget(self.view_table, 1,0,1,7)
        widget.setLayout(layout)
        return widget

    def view_delete(self):
        # Get the index of the currently selected row
        selected_row_index = self.view_table.currentRow()

        # Check if a row is actually selected (index will be -1 if none is)
        if selected_row_index >= 0:
            self.view_table.removeRow(selected_row_index)

    def view_clear_table(self):
        self.view_table.setRowCount(0)
        
    def view_search_client(self):
        self.global_message.appendPlainText("... view_search_client")
        fdlg = cnpfind.FindDialog(self.db_man.db, True)
        ret = fdlg.exec_()
        if ret == 1:
            clients = fdlg.get_clients()
            if clients is None or clients == []:
                msg.message_box("No client exist!", msg.message_warning)
                return
            else:
                self.view_list = clients
                #self.update_view_table()
                # client_list, view_table, visible_columns)
                cnpvtbl.update_view_table(self.view_list, self.view_table, self.visible_columns)
        
    def view_saveas_excel(self):
        
        if self.view_list is None or self.view_list == []:
            msg.message_box("No client to export", msg.message_warning)
            return
            
        self.global_message.appendPlainText("... view_saveas_excel")
            
        try:
            cnpexcel.export_clients_to_excel(
                    self.view_list,
                    self.visible_columns,
                    cnpconf.export_excel_fname,
                    cnpconf.export_title)
        except Exception as e:
            msg.message_box("Error: %s"%e)
            return
            
        msg.message_box(f"{len(self.view_list)} clients saved to {cnpconf.export_excel_fname}")
        
    def view_saveas_pdf(self):
        if self.view_list is None or self.view_list == []:
            msg.message_box("No client to export", msg.message_warning)
            return

        self.global_message.appendPlainText("... view_saveas_pdf")
            
        try:
            cnppdf.export_clients_to_pdf(
                    self.view_list,
                    self.visible_columns,
                    cnpconf.export_pdf_fname,
                    cnpconf.export_pdf_landscape,
                    cnpconf.export_title)
        except Exception as e:
            msg.message_box("Error: %s"%e)
            return
            
        msg.message_box(f"{len(self.view_list)} clients saved to {cnpconf.export_pdf_fname}")
        
    def change_view_setting(self):
        #self.show_customize_dialog()
        # view_table, all_columns, visible_columns, update_visible_column, gmsg):
        new_columns = cnpvtbl.show_customize_dialog(self.db_man.db,
                                      self.view_list,
                                      self.view_table, 
                                      self.all_columns, 
                                      self.visible_columns,
                                      cnpconf.update_visible_column,
                                      self.global_message)
        if new_columns is not None:
            self.visible_columns = new_columns

    def get_view_client(self):
        # create SQLite keys for search
        v_key = [f"{cnpdb.available_view_column_key(v_)}" for v_ in self.visible_columns]
        
        try:
            client_list = self.db_man.db.custom_query(v_key)
        except Exception as e:
            e_msg = f"... Error: clients from database\n{e}"
            msg.message_box(e_msg)
            self.global_message.appendPlainText(e_msg)
            return None
        
        if self.view_list == []: 
            return None
        return client_list
    
    def view_all_client(self):
        self.global_message.appendPlainText("... view_all_client")
        # create SQLite keys for search
        v_key = [f"{cnpdb.available_view_column_key(v_)}" for v_ in self.visible_columns]
        
        #self.view_list = self.db_man.db.load_all_clients()
        try:
            self.view_list = self.db_man.db.custom_query(v_key)
        except Exception as e:
            e_msg = f"... Error: clients from database\n{e}"
            msg.message_box(e_msg)
            self.global_message.appendPlainText(e_msg)
            return
        
        if self.view_list == []: 
            return
            
        cnpvtbl.update_view_table(self.view_list, self.view_table, self.visible_columns)
        #self.update_view_table()
        
    def set_picture_path(self, p):
        self.file_path.setText(p)
        
    def build_entry_tab(self):
        widget = QWidget()
        self.global_message.appendPlainText("... Build Entry Tab")
        main_layout = QHBoxLayout()
        #main_layout = QGridLayout()

        # --- LEFT PANEL (PICTURE AREA) ---
        left_panel = QVBoxLayout()
        
        self.picture_label = cnpdrag.DraggablePictureLabel() #QLabel("Drag and drop a picture here")
        self.picture_label.setAlignment(Qt.AlignCenter)
        self.picture_label.setStyleSheet("border: 2px dashed #aaa;")
        self.picture_label.setFixedSize(200, 200)
        self.picture_label.setAlignment(Qt.AlignCenter)
        self.picture_label.set_picture_path.connect(self.set_picture_path)

        pic_box = QGroupBox("Picture")
        pic_box.setAlignment(Qt.AlignCenter)
        pic_layout = QVBoxLayout()
        
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("File Path...")
        self.browse_button = QPushButton("Pick Picture")
        self.delete_button = QPushButton("Delete Picture")
        pic_layout.addWidget(self.file_path)
        pic_layout.addWidget(self.browse_button)
        pic_layout.addWidget(self.delete_button)
        pic_box.setLayout(pic_layout)
        
        self.browse_button.clicked.connect(self.pick_picture)
        self.delete_button.clicked.connect(self.delete_picture)
        
        left_panel.addWidget(self.picture_label)
        left_panel.addWidget(pic_box)

        # --- 
        db_box = QGroupBox("Database")
        db_box.setAlignment(Qt.AlignCenter)
        db_layout = QGridLayout()
        self.db_open = QPushButton()
        self.db_open.setIcon(QIcon(QPixmap(icon_folder_open.table)))
        self.db_open.setIconSize(QSize(32,32))
        self.db_open.setToolTip('Open client database\nNot implemented')
        
        self.db_save = QPushButton()
        self.db_save.setIcon(QIcon(QPixmap(icon_save.table)))
        self.db_save.setIconSize(QSize(32,32))
        self.db_save.setToolTip('Save As client database\nNot implemented')
        
        self.db_close = QPushButton()
        self.db_close.setIcon(QIcon(QPixmap(icon_logout.table)))
        self.db_close.setIconSize(QSize(32,32))
        self.db_close.setToolTip('Close client database\nNot implemented')
        
        self.db_export_word = QPushButton()
        self.db_export_word.setIcon(QIcon(QPixmap(icon_word.table)))
        self.db_export_word.setIconSize(QSize(32,32))
        self.db_export_word.clicked.connect(self.save_current_client_word)
        self.db_export_word.setToolTip('Export current client as Word file')

        self.db_export_excel = QPushButton()
        self.db_export_excel.setIcon(QIcon(QPixmap(icon_excel.table)))
        self.db_export_excel.setIconSize(QSize(32,32))
        self.db_export_excel.clicked.connect(self.save_current_client_excel)
        self.db_export_excel.setToolTip('Export current client as Excel file')

        self.db_arrow_btn = QPushButton()
        self.db_arrow_btn.setIcon(QIcon(QPixmap(icon_arrow_LR.table)))
        self.db_arrow_btn.setIconSize(QSize(32,32))
        self.db_arrow_btn.clicked.connect(self.enable_arrow_bottoms)
        self.db_arrow_btn.setToolTip('Enable prev/next arrow')
        
        self.db_search_house = QPushButton()
        self.db_search_house.setIcon(QIcon(QPixmap(icon_find.table)))
        self.db_search_house.setIconSize(QSize(32,32))
        self.db_search_house.clicked.connect(self.find_client)
        self.db_search_house.setToolTip('Search clients by name')

        self.db_search_birthday = QPushButton()
        self.db_search_birthday.setIcon(QIcon(QPixmap(icon_birthday.table)))
        self.db_search_birthday.setIconSize(QSize(32,32))
        self.db_search_birthday.clicked.connect(self.find_client_birthdat)
        self.db_search_birthday.setToolTip("Search clients' birthday")
        
        self.db_chart = QPushButton()
        self.db_chart.setIcon(QIcon(QPixmap(icon_chart.table)))
        self.db_chart.setIconSize(QSize(32,32))
        self.db_chart.clicked.connect(self.plot_chart)
        self.db_chart.setToolTip("Chart of Age")
        
        self.db_delete_all_btn = QPushButton()
        self.db_delete_all_btn.setIcon(QIcon(QPixmap(icon_clear.table)))
        self.db_delete_all_btn.setIconSize(QSize(32,32))
        self.db_delete_all_btn.clicked.connect(self.delete_all_clients)
        self.db_delete_all_btn.setToolTip("Delete All Clients")

        self.db_fetch_all = QPushButton()
        self.db_fetch_all.setIcon(QIcon(QPixmap(icon_fetch_all.table)))
        self.db_fetch_all.setIconSize(QSize(32,32))
        self.db_fetch_all.clicked.connect(self.load_all_clients)
        self.db_fetch_all.setToolTip('Load all clients')
        
        db_layout.addWidget(self.db_open, 0,0)
        db_layout.addWidget(self.db_save, 0,1)
        db_layout.addWidget(self.db_close, 0,2)
        db_layout.addWidget(self.db_export_word, 1,0)
        db_layout.addWidget(self.db_export_excel, 1,1)
        db_layout.addWidget(self.db_arrow_btn, 1,2)
        db_layout.addWidget(self.db_search_house, 2,0)
        db_layout.addWidget(self.db_search_birthday, 2,1)
        db_layout.addWidget(self.db_chart, 2,2)
        db_layout.addWidget(self.db_fetch_all, 3,0)
        db_layout.addWidget(self.db_delete_all_btn, 3,1)
        db_box.setLayout(db_layout)
        left_panel.addWidget(db_box)
        
        # --- RIGHT PANEL (DATA AREA) ---
        right_panel = QVBoxLayout()

        # Names\
        self.name_box = QGroupBox("Names")
        name_layout = QGridLayout()
        
        self.first_name_kr = QLineEdit() 
        self.last_name_kr = QLineEdit()
        self.first_name_kr.setPlaceholderText("First Name")
        self.last_name_kr .setPlaceholderText("Last Name")
        
        self.first_name_en = QLineEdit() 
        self.middle_name_en = QLineEdit() 
        self.last_name_en  = QLineEdit()
        
        self.first_name_en.setPlaceholderText("First Name")
        self.middle_name_en.setPlaceholderText("Middle Name")
        self.last_name_en.setPlaceholderText("Last Name")
        
        name_layout.addWidget(QLabel(""), 0,0)
        name_layout.addWidget(QLabel("First"), 0,1)
        name_layout.addWidget(QLabel("Middle"), 0,2)
        name_layout.addWidget(QLabel("Last"), 0,3)   
        
        name_layout.addWidget(QLabel("Korean"), 1,0)
        name_layout.addWidget(self.first_name_kr, 1,1) 
        name_layout.addWidget(self.last_name_kr,1,3)
        
        name_layout.addWidget(QLabel("English"),2,0)
        name_layout.addWidget(self.first_name_en,2,1)
        name_layout.addWidget(self.middle_name_en,2,2)
        name_layout.addWidget(self.last_name_en,2,3)

        self.dob = QDateEdit(); 
        self.dob.setCalendarPopup(True)
        self.dob.dateChanged.connect(self.calculate_age)
        self.age = QLineEdit()
        self.age.setEnabled(False)
        self.sex = QComboBox()
        self.sex.addItems(["Male", "Female"])
        
        name_layout.addWidget(QLabel("DOB"),3,1); 
        name_layout.addWidget(QLabel("AGE"),3,2); 
        name_layout.addWidget(QLabel("SEX"),3,3); 
        
        name_layout.addWidget(self.dob,4,1)
        name_layout.addWidget(self.age,4,2)
        name_layout.addWidget(self.sex,4,3)
        
        self.name_box.setLayout(name_layout)
        right_panel.addWidget(self.name_box, 1)
        
        # Dates
        date_layout = QGridLayout()
        date_box = QGroupBox("Date")
        
        self.initial_assessment = QLineEdit()
        self.initial_assessment_btn = QPushButton("📅")  # calendar button
        self.initial_assessment_btn.setFixedWidth(30)
        
        self.initial_assessment_date = QCalendarWidget(self)
        self.initial_assessment_date.setWindowFlags(Qt.Popup)
        self.initial_assessment_date.setGridVisible(True)
        self.initial_assessment_date.clicked.connect(self.update_assessment_date)

        self.initial_assessment_btn.clicked.connect(partial(self.show_calendar, self.initial_assessment_btn, self.initial_assessment_date))
        
        self.assessment_14th = QLineEdit()         
        self.assessment_90th = QLineEdit() 
        
        self.change_assessment = QLineEdit() 
        self.change_assessment_check = QCheckBox("Done") 
        
        self.change_assessment_date = QCalendarWidget(self)
        self.change_assessment_date.setWindowFlags(Qt.Popup)
        self.change_assessment_date.setGridVisible(True)
        self.change_assessment_date.clicked.connect(self.update_change_assessment_date)
        
        self.change_assessment_btn = QPushButton("📅")  # calendar button
        self.change_assessment_btn.setFixedWidth(30)
        self.change_assessment_btn.clicked.connect(partial(self.show_calendar, self.change_assessment_btn, self.change_assessment_date))
        
        date_layout.addWidget(QLabel("Initial Assessment"),0,0) 
        date_layout.addWidget(self.initial_assessment,0,1) 
        date_layout.addWidget(self.initial_assessment_btn,0,2) 
        
        date_layout.addWidget(self.initial_assessment, 0,1)
        date_layout.addWidget(QLabel("14th Assessment"),1,0) 
        date_layout.addWidget(self.assessment_14th,1,1) 

        date_layout.addWidget(QLabel("90th Assessment"),2,0) 
        date_layout.addWidget(self.assessment_90th,2,1) 
        
        date_layout.addWidget(QLabel("Change Assessment"),3,0) 
        date_layout.addWidget(self.change_assessment,3,1) 
        date_layout.addWidget(self.change_assessment_btn,3,2) 
        date_layout.addWidget(self.change_assessment_check,3,3) 
        
        date_box.setLayout(date_layout)
        right_panel.addWidget(date_box,2)

        # Room
        room_layout = QHBoxLayout()
        #room_layout = QGridLayout()
        self.room_number = QLineEdit()
        #right_panel.addWidget(QLabel("Room Number"))
        #right_panel.addWidget(self.room_number)
        
        self.floor_2_button = QPushButton("")
        self.floor_2_button.setIcon(QIcon(QPixmap(icon_num_blue_02.table)))
        self.floor_2_button.setIconSize(QSize(16,16))
        self.floor_2_button.clicked.connect(self.choose_room_floor_02)
         
        self.floor_3_button = QPushButton("")
        self.floor_3_button.setIcon(QIcon(QPixmap(icon_num_blue_03.table)))
        self.floor_3_button.setIconSize(QSize(16,16))
        self.floor_3_button.clicked.connect(self.choose_room_floor_03)

        self.floor_4_button = QPushButton("")
        self.floor_4_button.setIcon(QIcon(QPixmap(icon_num_blue_04.table)))
        self.floor_4_button.setIconSize(QSize(16,16))
        self.floor_4_button.clicked.connect(self.choose_room_floor_04)

        room_layout.addWidget(QLabel("Room Number"))
        room_layout.addWidget(self.room_number)
        room_layout.addWidget(self.floor_2_button)
        room_layout.addWidget(self.floor_3_button)
        room_layout.addWidget(self.floor_4_button)
        
        #room_layout.addWidget(self.room_number, 0, 0)
        #room_layout.addWidget(self.floor_2_button, 0, 1)
        #room_layout.addWidget(self.floor_3_button, 0, 2)
        #room_layout.addWidget(self.floor_4_button, 0, 3)

        right_panel.addLayout(room_layout)
        
        # Comments
        right_panel.addWidget(QLabel("Comments"))
        self.comments = QTextEdit()
        right_panel.addWidget(self.comments)

        # Action Buttons
        button_row = QHBoxLayout()
        self.add_button = QPushButton("")
        self.add_button.setIcon(QIcon(QPixmap(icon_save_01.table)))
        self.add_button.setIconSize(QSize(32,32))
        self.add_button.clicked.connect(self.save_client)
        self.add_button.setToolTip("(1) Save a new client\n(2) Updae current client")
        
        self.new_button = QPushButton("")
        self.new_button.setIcon(QIcon(QPixmap(icon_add.table)))
        self.new_button.setIconSize(QSize(32,32))
        self.new_button.clicked.connect(self.new_client)
        self.new_button.setToolTip("(1) Clear entry\n(2) Add a new client")
        
        self.update_button = QPushButton("")
        self.update_button.setIcon(QIcon(QPixmap(icon_update.table)))
        self.update_button.setIconSize(QSize(32,32))
        self.update_button.clicked.connect(self.update_client)
        
        self.remove_button = QPushButton("")
        self.remove_button.setIcon(QIcon(QPixmap(icon_delete.table)))
        self.remove_button.setIconSize(QSize(32,32))
        self.remove_button.clicked.connect(self.remove_client)
        self.remove_button.setToolTip("Delete current client")
        
        self.prev_button = QPushButton("")
        self.prev_button.setIcon(QIcon(QPixmap(icon_arrow_left.table)))
        self.prev_button.setIconSize(QSize(32,32))
        self.prev_button.clicked.connect(self.previous_client)
        
        self.next_button = QPushButton("")
        self.next_button.setIcon(QIcon(QPixmap(icon_arrow_right.table)))
        self.next_button.setIconSize(QSize(32,32))
        self.next_button.clicked.connect(self.next_client)

        self.direction_button(False)
        
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.new_button)
        button_row.addWidget(self.remove_button)
        button_row.addWidget(self.prev_button)
        button_row.addWidget(self.next_button)

        right_panel.addLayout(button_row)

        # --- Final Layout ---
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)
        
        widget.setLayout(main_layout)
        return widget

        # Connections
        #self.save_button.clicked.connect(self.save_client)
        #self.find_button.clicked.connect(self.find_client)
        #self.delete_button2.clicked.connect(self.delete_client)
    
    def plot_chart(self):
        import cnpchart
        
        cnpchart.create_client_chart(self.db_man, self.global_message)
        
    def find_client_birthdat(self):
        import cnpbirthday
        
        cnpbirthday.search_birthday(self.db_man, self.global_message)
        
    def enable_arrow_bottoms(self):
        self.direction_button(True)
        
    def delete_all_clients(self):
    
        res = msg.message_box("Do you want to removel all clients?", msg.message_yesno)
        if res == QMessageBox.No: return         
    
        try:
            deleted_clients = self.db_man.db.remove_all()
        except Exception as e:
            msg.message_box(f"{e}", msg.message_warning)
            
        msg.message_box(f"{deleted_clients} clients deleted!")
        self.db_man.clear()
        self.clear_entry()
            
    def save_current_client_(self, word=True):
        self.global_message.appendPlainText("... save_current_client: %s"%("WORD" \
        if word else "EXCEL"))
        
        if self.get_client_id() is None:
            msg.message_box("No client ID found!!", msg.message_warning)
            return
            
        f_ = cnpconf.save_word_fname_cur_client if word \
             else cnpconf.save_excel_fname_cur_client
        c_ = self.db_man.current_client()
        
        try:
            if word:
                cnpword.save_client_to_word(c_, f_)
            else:
                cnpexcel.save_client_to_excel(c_, f_)
        except Exception as e:
            self.global_message.appendPlainText(f"... Error: save {f_} => {e}")
            msg.message_box(f"Error: {e}", msg.message_error)
            return
        msg.message_box(f"Save current client : {f_}")
    
    def save_current_client_excel(self):
        self.save_current_client_(False)
        
    def save_current_client_word(self):
        self.save_current_client_(True)

    def set_selected_room(self, selected_item):
        self.selected_client_room = selected_item
        if self.selected_client_room is None:
            return
        clients = self.db_man.get_clients()
        
        if clients is None:
            msg.message_box("No clients!\nLoad clients!!")
            return
            
        for c_ in clients:
            if c_[cnpdb.col_room_number] == self.selected_client_room:
                self.clear_entry()
                self.show_current_client(c_)
                break
        self.direction_button(False)

    def choose_room_floor(self, button, floor):
        self.selected_client_room = None
        client = self.db_man.db.search_by_rooms(floor)
        if client == []:
            msg.message_box(f"No client on {floor[0:1]} floor", msg.message_warning)
            return False
            
        room = [r_[cnpdb.col_room_number] for r_ in client]
        popup = cnpcomb.PopupCombo(self, sorted(room))
        popup.set_current_item.connect(self.set_selected_room)
        # place the popup just right beside the button
        btn_pos = button.mapToGlobal(QPoint(button.width(), 0))
        popup.move(btn_pos)
        #popup.show()
        popup.combo.showPopup()
        popup.combo.setFocus()
        
    def choose_room_floor_02(self):
        self.choose_room_floor(self.floor_2_button, "2%")

    def choose_room_floor_03(self):
        self.choose_room_floor(self.floor_3_button, "3%")
        
    def choose_room_floor_04(self):
        self.choose_room_floor(self.floor_4_button, "4%")
    
    def find_client(self):
        self.direction_button(False)
        fdlg = cnpfind.FindDialog(self.db_man.db)
        ret = fdlg.exec_()
        
        if ret == 1:
            c_ = fdlg.selected_client()
            if c_ is None: return
            self.direction_button(False)
            self.clear_entry()
            self.show_current_client(c_)
    
    def load_all_clients(self):
        #self.global_message.appendPlainText(f"... load_all_clients")
        self.fetch_all_clients()
        self.show_current_client()
        
    def fetch_all_clients(self):
        #self.global_message.appendPlainText(f"... fetch_all_clients")
        self.clear_entry()
        
        try:
            self.db_man.load()
        except Exception as e:
            e_msg = f"... Error: {e}"
            self.global_message.appendPlainText(e_msg)
            msg.message_box(e_msg)
            
        self.direction_button(True)
        
    def choose_room_number(self):
        self.global_message.appendPlainText("... choose_room_number")
        rdlg = QChooseRoomNumberDlg(self.db_man.db)
        ret = rdlg.exec_()
        if ret == 1:
            r_ = rdlg.get_current_room()
            c_ = self.db_man.db.search_by_room(r_)
            if len(c_) > 1:
                #self.global_message.
                msg.message_box("Error : duplicate room numbers. See messages.", msg.message_error)
            
    def clear_entry(self):
        #self.global_message.appendPlainText("... clear_entry")
        self.delete_picture()
        self.picture_label.setText("Drag and drop a picture here\n(or use 'Browse')")
        self.name_box.setTitle("Name: ")
        self.file_path     .setText("")   
        self.first_name_kr .setText("")   
        self.last_name_kr  .setText("")   
        self.first_name_en .setText("")   
        self.middle_name_en.setText("")   
        self.last_name_en  .setText("")  

        self.dob.setDate(QDate.currentDate())
        self.age.setText("")
        self.sex.setCurrentIndex(0)
        
        self.room_number       .setText("")
        self.initial_assessment.setText("")
        self.assessment_14th   .setText("")
        self.assessment_90th   .setText("")
        self.change_assessment .setText("")
        self.change_assessment_check.setChecked(False)
        self.comments.setPlainText("")
        
    def sex_initial(self):
        return self.sex.currentText()[0:1]
        
    def client_data(self):
        return self.new_client_data(False)
        
    def new_client_data(self, new=True):
        #self.global_message.appendPlainText("... new_client_data")
        date_string = self.dob.date().toString(cnpval.date_format_r)
        s_ = self.change_assessment_check.isChecked()
        x_ = self.sex_initial()
        r_ = self.room_number.text()
        if new:
            i_ = self.db_man.cim.get(cnpval.state, cnpval.building_number)
        else:
            i_ = self.get_client_id()
            if i_ is None:
                msg.message_box("Error: invalid client data(No ID)")
                return None

        client = {
            cnpdb.col_id                    : i_,
            cnpdb.col_pic_path              : self.file_path     .text() or None,
            cnpdb.col_first_name_kor        : self.first_name_kr .text() or None,
            cnpdb.col_last_name_kor         : self.last_name_kr  .text() or None,
            cnpdb.col_first_name_eng        : self.first_name_en .text() or None,
            cnpdb.col_middle_name_eng       : self.middle_name_en.text() or None,
            cnpdb.col_last_name_eng         : self.last_name_en  .text() or None,
            cnpdb.col_dob                   : date_string  or None,
            cnpdb.col_sex                   : x_ or None,
            cnpdb.col_room_number           : r_ or None,
            cnpdb.col_initial_assessment    : self.initial_assessment.text() or None,
            cnpdb.col_assessment_14th       : self.assessment_14th.text() or None,
            cnpdb.col_assessment_90th       : self.assessment_90th.text() or None,
            cnpdb.col_change_assessment     : self.change_assessment.text() or None,
            cnpdb.col_change_assessment_done: cnpdb.change_assessment_yes if s_ == True else \
                                              cnpdb.change_assessment_no,
            cnpdb.col_comments              : self.comments.toPlainText() or None
        }
        
        return client
        
    def new_client(self):
        #self.global_message.appendPlainText("... new_client(add)")
        self.clear_entry()
        
    def direction_button(self, enabled=False):
        self.next_button.setEnabled(enabled)
        self.prev_button.setEnabled(enabled)
        
    def save_client(self):
        self.global_message.appendPlainText("... save_client")

        if not (self.first_name_kr.text() or self.first_name_en.text()):
            QMessageBox.warning(self, "Validation Error", 
            "At least one name (Korean or English) is required.")
            return
        
        r_ = re.match(cnpval.room_number_f, self.room_number.text())
        if r_ is None:
            msg.message_box("Error: invalid room number", msg.message_error)
            return
        
        i_ = self.get_client_id()
        
        if i_ is None:
            c_ = self.new_client_data()
            self.global_message.appendPlainText(f"... Add client: {c_[cnpdb.col_id]}")
            try:
                self.db_man.add_client(c_)
            except Exception as e:
                e_msg = f"Warning: {e}"
                self.global_message.appendPlainText(e_msg)
                msg.message_box(e_msg, msg.message_warning)
                self.db_man.cim.discard(c_[cnpdb.col_id])
                return
                
            self.name_box.setTitle(f"Name: ID({c_[cnpdb.col_id]})")
            self.fetch_all_clients()
            self.db_man.end_client()
            self.show_current_client()
        else:
            if self.db_man.db.check_client_id_exists(i_):
                res = msg.message_box("Do you want to save?", msg.message_yesno)
                if res == QMessageBox.No: return 
                try:
                    self.db_man.update_client(self.client_data())
                except Exception as e:
                    e_msg = f"Error: can't save client data. {e}"
                    self.global_message.appendPlainText(e_msg)
                    msg.message_box(e_msg, msg.message_error)
                    return
                
    def remove_client(self):
        self.global_message.appendPlainText("... remove_client")
        
        i_ = self.get_client_id()
        
        if i_ is None: return
        else:
            res = msg.message_box("Do you want to remove current client?", msg.message_yesno)
            if res == QMessageBox.No: 
                return 
            
            try:
                self.db_man.delete_client(i_)
            except Exception as e:
                e_msg = f"... Error: {e}"
                self.global_message.appendPlainText(e_msg)
                msg.message_box(e_msg, msg.message_warning)
                return
            #self.clear_entry()
            #self.direction_button(False)
            prv_client_index = self.db_man.cur_client_index
            self.fetch_all_clients()
            self.db_man.calculate_client_index(prv_client_index)
            self.show_current_client()
            
            e_msg=f"... Delete ID({i_}) success"
            self.global_message.appendPlainText(e_msg)
            msg.message_box(e_msg)
        
    def update_client(self):
        self.global_message.appendPlainText("... update_client")
        i_ = self.get_client_id()
        if i_ is None:
            e_msg = "... Error: No ID exist. If this is a new client, click SAVE"
            self.global_message.appendPlainText(e_msg)
            msg.message_box(e_msg, msg.message_warning)
            return
            
        try:
            self.db_man.update_client(self.client_data())
        except Exception as e:
            e_msg = f"... Error: {e}"
            self.global_message.appendPlainText(e_msg)
            msg.message_box(e_msg, msg.message_warning)
        
    def get_client_id(self):
        #self.global_message.appendPlainText("... get_client_id")
        m_ = re.search(cnpval.id_f, self.name_box.title())
        if m_: 
            return m_.group(1)
        else:
            return None
        
    def delete_client(self):
        self.global_message.appendPlainText("... delete_client")
        id_ = self.get_client_id()
        if id_ is None:
            msg.message_box("... Error: No ID exist", msg.message_warning)
            return
            
        ret = msg.message_box("Do you want to delete?", msg.yesno)
        if ret == QMessageBox.No:
            return
            
        try: 
            self.db_man.delete_client(id_)
        except Exception as e:
            msg.message_box(f"Error: {e}")
            return 
        e_msg = f"Deletion complete(ID: {id_}"
        self.global_message.appendPlainText(e_msg)
            
        self.clear_entry()
        prv_client_index = self.db_man.cur_client_index
        self.fetch_all_clients()
        self.db_man.calculate_client_index(prv_client_index)
        self.show_current_client()
        
        msg.message_box(e_msg)
        
    def previous_client(self):
        if self.db_man.prev_client():
            if not self.next_button.isEnabled():
                self.next_button.setEnabled(True)
            self.clear_entry()
            self.show_current_client()
        else:
            self.prev_button.setEnabled(False)
        
    def next_client(self):
        if self.db_man.next_client():
            if not self.prev_button.isEnabled():
                self.prev_button.setEnabled(True)
            self.clear_entry()
            self.show_current_client()
        else:
            self.next_button.setEnabled(False)
        
    def show_calendar(self, btn, cal):
        # Position the calendar below the button
        pos = btn.mapToGlobal(btn.rect().bottomRight())
        cal.move(pos)
        cal.show()

    def pick_picture(self):
        file, _ = QFileDialog.getOpenFileName(self, "Pick a picture", "", "Images (*.png *.jpg *.bmp)")
        if file:
            self.file_path.setText(file)
            pixmap = QPixmap(file).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.picture_label.setPixmap(pixmap)

    def delete_picture(self):
        self.file_path.clear()
        self.picture_label.setPixmap(QPixmap())
        self.picture_label.setText("Drag and drop a picture here")

    def update_assessment_date(self, date):
        self.initial_assessment.setText(date.toString("MM/dd/yyyy, (ddd)"))
        self.assessment_14th.setText(date.addDays(14).toString("MM/dd/yyyy, (ddd)"))
        self.assessment_90th.setText(date.addDays(90).toString("MM/dd/yyyy, (ddd)"))
        
    def update_change_assessment_date(self, date):
        self.change_assessment.setText(date.toString("MM/dd/yyyy, (ddd)"))

    def calculate_age(self):
        age = cnputil.calculate_age(self.dob.date())
        self.age.setText(f"Age: {age}")
    '''    
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Left, Qt.Key_Right):
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                # ---- Shift+Arrow : navigate tabs ----
                current = self.tabs.currentIndex()
                if event.key() == Qt.Key_Left and current > 0:
                    self.tabs.setCurrentIndex(current - 1)
                elif event.key() == Qt.Key_Right and current < self.tabs.count() - 1:
                    self.tabs.setCurrentIndex(current + 1)
            else:
                # ---- Just Arrow : navigate clients ----
                if self.tabs.currentIndex() == 0:  # only in first tab
                    if event.key() == Qt.Key_Left:
                        if self.prev_button.isEnabled():
                            print("prev")
                            self.prev_client()
                        #self.client_index -= 1
                    else:
                        if self.next_button.isEnabled():
                            print("next")
                            self.next_client()
                        self.client_index += 1
                    #self.client_label.setText(f"Client: {self.client_index}")
        else:
            super().keyPressEvent(event)
    '''
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = MainWindow()
    window.resize(600, 500)
    window.show()
    sys.exit(app.exec_())
