'''
    cnpchart.py
    9/8/2025
    AI : gemini

'''
from collections import defaultdict
import xlsxwriter 

from PyQt5.QtWidgets import (
     QPushButton   , QHBoxLayout   , QVBoxLayout, 
     QDialog      , QFormLayout   , QComboBox,
     QGridLayout, QCheckBox, QLabel
)

from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import QPixmap, QIcon

import msg, color
import cnpdb, cnpval, cnpconf, cnpvtbl, msg, cnpval, cnputil
import icon_system, icon_view_setting, icon_chart_bar, \
       icon_chart_pie
      
_bar_chart_fname = "Age-bar-chart.xlsx"      
_pie_chart_fname = "Age-pie-chart.xlsx"
_age_interval = 5
      
class QChartDlg(QDialog):
    def __init__(self, db_man, gmsg):
        super(QChartDlg, self).__init__()
        self.db_man = db_man
        self.client_list = None
        self.gmsg = gmsg
        m_layout = QGridLayout()
        
        self.bar_chart = QCheckBox()
        self.bar_chart.setIcon(QIcon(QPixmap(icon_chart_bar.table)))
        self.bar_chart.setIconSize(QSize(32,32))
        
        self.pie_chart = QCheckBox()
        self.pie_chart.setIcon(QIcon(QPixmap(icon_chart_pie.table)))
        self.pie_chart.setIconSize(QSize(32,32))
        
        self.ok = QPushButton('OK')
        self.cancel = QPushButton('CANCEL')
        
        self.ok.clicked.connect(self.create_chart)
        self.cancel.clicked.connect(self.reject)
        
        m_layout.addWidget(self.bar_chart, 0,0)
        m_layout.addWidget(QLabel("Individual Age"), 0,1)
        m_layout.addWidget(self.pie_chart, 1,0)
        m_layout.addWidget(QLabel("Age Distribution"), 1,1)
        m_layout.addWidget(self.ok, 2,0)
        m_layout.addWidget(self.cancel, 2,1)
        self.setLayout(m_layout)
        self.setWindowTitle("Chart")
        self.setWindowIcon(QIcon(QPixmap(icon_system.table)))

    def create_chart(self):
        if not any([self.bar_chart.isChecked(), self.pie_chart.isChecked()]):
            msg.message_box("Chose at least one option")
            return
        
        key = [cnpdb.col_id, cnpdb.col_dob]
        
        try:
            clients = self.db_man.db.load_all_clients(key)
        except Exception as e:
            e_msg = f"cnpchart.py (create_chart): {e}"
            self.gmsg.appendPlainText(e_msg)
            msg.message_box(e_msg)
            return
        
        if clients == []:
            e_msg = "cnpchart.py (create_chart): No clients!!"
            self.gmsg.appendPlainText(e_msg)
            msg.message_box(e_msg)
            return
        
        client_data = []
        for c_ in clients:
            i_ = c_[cnpdb.col_id][-3:]
            d_ = c_[cnpdb.col_dob][0:10] # get only MM/dd/yyyy
            new_date = QDate.fromString(d_, cnpval.date_format_w)
            client_data.append([i_, cnputil.calculate_age(new_date)])
            
        if self.bar_chart.isChecked():
            try:
                # Create workbook and worksheet
                workbook = xlsxwriter.Workbook(_bar_chart_fname)
                worksheet = workbook.add_worksheet("Individual Age")
        
                # Write client data (names + ages)
                for row_idx, row_data in enumerate(client_data):
                    worksheet.write(row_idx, 0, row_data[0])  # Name
                    worksheet.write(row_idx, 1, row_data[1])  # Age
        
                # Create bar/column chart
                chart = workbook.add_chart({'type': 'column'})
        
                # Add data series
                chart.add_series({
                    'name':       'Client Ages',
                    'categories': ['Individual Age', 0, 0, len(client_data)-1, 0],  # Names
                    'values':     ['Individual Age', 0, 1, len(client_data)-1, 1],  # Ages
                    'fill':       {'color': '#4472C4'},  # Bar color
                    'border':     {'color': '#2E5A87'},  # Border color
                })
        
                # Set axis titles
                chart.set_x_axis({'name': 'Client'})
                chart.set_y_axis({'name': 'Age'})
        
                # Chart title
                chart.set_title({'name': 'Client Ages'})
        
                # Insert chart into worksheet
                worksheet.insert_chart('E2', chart)
        
                workbook.close()
                workbook = None
            except Exception as e:
                e_msg = f"Error: Pie Chart\n{e}"
                self.gmsg.appendPlainText(e_msg)
                msg.message_box(e_msg)
                return
            
        if self.pie_chart.isChecked():
            try:
                workbook = xlsxwriter.Workbook(_pie_chart_fname)
                worksheet = workbook.add_worksheet("Individual Age")
                    
                ages = [a_[1] for a_ in client_data]
                # Use a defaultdict to simplify counting
                age_groups = defaultdict(int)
            
                # Find the minimum age to determine the starting group
                min_age = min(ages)
                
                # Calculate the starting point for the first group
                start_group = (min_age // _age_interval) * _age_interval
            
                # Find the maximum age to determine the final group
                max_age = max(ages)
                
                # Iterate through all ages and count them into their respective groups
                for age in ages:
                    # Determine the start of the 5-year _age_interval for the current age
                    group_start = (age // _age_interval) * _age_interval
                    group_end = group_start + _age_interval - 1
                    
                    # Create the group label (e.g., "20-24")
                    group_label = f"{group_start}-{group_end}"
                    
                    # Increment the count for this group
                    age_groups[group_label] += 1
                
                age_groups = {group: count for group, count in age_groups.items() if count > 0}

                # --- Write header and data to sheet ---
                worksheet.write(0, 0, "Age Group")
                worksheet.write(0, 1, "Count")
                # Write rows starting at row 1
                for i, (group, count) in enumerate(age_groups.items(), start=1):
                    worksheet.write(i, 0, group)
                    worksheet.write(i, 1, count)
        
                num_slices = len(age_groups)
        
                # --- Generate hex color list ---
                hex_colors = None
        
 
                colormap = color.create_color_table(0, 190, 0.5, 1, num_slices)
                # Expect objects with .r, .g, .b ints 0-255
                hex_colors = [f'#{c_.r:02x}{c_.g:02x}{c_.b:02x}' for c_ in colormap]

                # 3) Fallback: simple HSV-based generator (no external deps)
                if hex_colors is None:
                    hex_colors = []
                    for i in range(num_slices):
                        # vary hue across a subset to avoid too-green-only palettes
                        hue = (i / max(1, num_slices)) * 0.8  # 0..0.8 of hue wheel
                        r, g, b = colorsys.hsv_to_rgb(hue, 0.6, 0.95)
                        hex_colors.append('#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255)))
        
                # --- Create the pie chart and apply colors per-slice ---
                chart = workbook.add_chart({'type': 'pie'})
        
                # Construct 'points' list for custom slice colors
                points = [{'fill': {'color': color_hex}} for color_hex in hex_colors]
        
                # Add series: data rows are from row 1 to row 1+num_slices-1
                chart.add_series({
                        'name':       'Client Age Group Distribution',
                        'categories': ['Individual Age', 1, 0, num_slices, 0],
                        'values':     ['Individual Age', 1, 1, num_slices, 1],
                        'points':     points,
                        'data_labels': {
                        'percentage': True,
                        'category': True,
                        'value': True,
                        'leader_lines': True
                    },
                })
        
                chart.set_title({'name': 'Client Age Group Distribution'})
        
                # Insert chart (same placement as your original)
                worksheet.insert_chart('D2', chart)
                workbook.close()
                workbook = None
            except Exception as e:
                e_msg = f"Error: Pie Chart\n{e}"
                self.gmsg.appendPlainText(e_msg)
                msg.message_box(e_msg)
                return
        self.accept()
        
def create_client_chart(db_man, gmsg):
    
    b_ = QChartDlg(db_man, gmsg)
    ret = b_.exec_()
