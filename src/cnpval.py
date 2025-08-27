'''
    cnpval.py
'''
import re

date_format_r = "MM/dd/yyyy (ddd)"
date_format_w = "MM/dd/yyyy"

building_number = 0
state = "GA"

room_number_f = r'^\d{1,3}'

id_f = r'\((.*?)\)'