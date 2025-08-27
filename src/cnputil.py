'''
cnputil.py
'''
from PyQt5.QtCore import QDate

def calculate_age(dob):
    #dob = dob.date()
    today = QDate.currentDate()
    age = today.year() - dob.year()
    
    # Adjust age if the birthday hasn't occurred this year yet
    if today.month() < dob.month() or \
    (today.month() == dob.month() and today.day() < dob.day()):
        age -= 1
        
    return age
    
def safe_val(v):
    return "" if v is None else str(v)    