'''
    cnpconf.py
'''
import os

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