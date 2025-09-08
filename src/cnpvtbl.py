from PyQt5.QtWidgets import (
        QTableWidgetItem, QDialog
     )
import cnpcusttbl, cnpconf, cnpdb

def update_view_table(client_list, view_table, visible_columns):
    #global_message.appendPlainText("... update_view_table")
    # Clear the old table
    view_table.clear()
    
    # Set new column count and headers
    view_table.setColumnCount(len(visible_columns))
    view_table.setHorizontalHeaderLabels(visible_columns)
    
    if client_list is not None:
        # Populate the table with data
        view_table.setRowCount(len(client_list))
        for row_idx, row_data in enumerate(client_list):
            for col_idx, col_name in enumerate(visible_columns):
                key = cnpdb.available_view_column_key(col_name)
                value = row_data.get(key, "")
                view_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    
    view_table.resizeColumnsToContents()
    view_table.horizontalHeader().setStretchLastSection(True)

def show_customize_dialog(client_list, view_table, all_columns, visible_columns, update_func, msg):
    # Create a list of currently selected columns and available columns
    available = [col for col in all_columns if col not in visible_columns]
    
    dialog = cnpcusttbl.CustomizeTableDlg(available, visible_columns)
    
    # Show the dialog and get the result
    if dialog.exec_() == QDialog.Accepted:
        new_visible_columns = dialog.get_selected_columns()
        update_visible_column = False
        v1_ = visible_columns
        v2_ = new_visible_columns
        
        if len(v1_) <= len(v2_):
            v1_, v2_ = v2_, v1_
        
        for v_ in v1_:
            if v_ in v2_:
                continue
            else:
                update_visible_column = True
                break
                
        visible_columns = new_visible_columns      
        update_view_table(client_list, view_table, visible_columns)

        if update_visible_column:
            update_func(new_visible_columns, msg)
            cnpconf.save_config(msg)
