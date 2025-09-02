'''
    cnpconf.py
'''
from collections import OrderedDict
import os, json
from pathlib import Path
import cnpdb

export_pdf_fname = "export_client.pdf"
export_excel_fname = "export_client.xlsx"
export_pdf_landscape = "Landscape"
export_pdf_portrait = "Portrait"
export_title = "Client List"

save_word_fname_cur_client = "eben_client.docx"
save_excel_fname_cur_client = "eben_client.xlsx"

font_folder_path = os.path.join(os.environ['SystemRoot'], 'Fonts')
pdf_kfont = 'batang.ttc'
pdf_kfont_file = os.path.join(font_folder_path,pdf_kfont)

floor02_start, floor02_end = 200, 240
floor03_start, floor03_end = 300, 340
floor04_start, floor04_end = 400, 440

visible_column_key = "Visible Column"

default_visible_columns = [
    cnpdb.view_table_head_label[cnpdb.last_name_kor_index],
    cnpdb.view_table_head_label[cnpdb.first_name_kor_index],
    cnpdb.view_table_head_label[cnpdb.last_name_eng_index],
    cnpdb.view_table_head_label[cnpdb.first_name_eng_index],
    cnpdb.view_table_head_label[cnpdb.room_number_index],
    cnpdb.view_table_head_label[cnpdb.sex_index],
    cnpdb.view_table_head_label[cnpdb.initial_assessment_index],
    cnpdb.view_table_head_label[cnpdb.assessment_14th_index],
    cnpdb.view_table_head_label[cnpdb.assessment_90th_index],
    cnpdb.view_table_head_label[cnpdb.change_assessment_index],
    cnpdb.view_table_head_label[cnpdb.change_assessment_done_index]
]

default_config = {
    visible_column_key : default_visible_columns
}

visible_columns = [c_ for c_ in default_visible_columns]

config = {
    visible_column_key : visible_columns
}

config_file = "cnp.ini"

def update_visible_column(new_visible_column, msg):
    global config
    config[visible_column_key] = new_visible_column
    save_config(msg)
    
def load_config(msg):
    global config
    
    p = Path(config_file)
    # check config file exist. if no create config file
    if p.exists() == False:
        msg.appendPlainText("... No config exists. Creating a new one(cnp.ini)")
        with open(config_file, "wt") as fp:
            json.dump(default_config, fp, ensure_ascii=False, indent=4)
    else:
        msg.appendPlainText("... Loading config (cnp.ini)")
        try:
            with open(config_file, "rt") as fp:
                config = json.load(fp)
        except Exception as e:
            msg.appendPlainText(f"... Fail to load(cnp.ini): {e}")
            
def get_visible_columns():
    return config[visible_column_key]
    
def save_config(msg):
    msg.appendPlainText(f"... Save config(cnp.ini)")
    try:
        with open(config_file, "wt") as fp:
            json.dump(config, fp, ensure_ascii=False, indent=4)
    except Exception as e:
        msg.appendPlainText(f"... Fail to save(cnp.ini): {e}")
        
if __name__ == "__main__":
    load_config()