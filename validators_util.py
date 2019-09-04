import re
import phonenumbers as phn
# from phonenumbers import COUNTRY_CODE_TO_REGION_CODE

import validators

def valid_email(val):
    """simple email validation - to consider using python validate_email - existence is possible"""

    if not val:
        return False
    # more complex email validator
    # return bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", val))
    if not validators.email(val):
        return False
    return True

    #from validate_email import validate_email
    #return validate_email(val,verify=True)


def validate_phone(val):
    if not val:
        return False, None, None, False
    try:
        num = phn.parse('+'+val,None)
        return True, str(num.country_code), str(num.national_number), phn.is_possible_number(num)
    except:
        return False, None, None, False

def subtract_name(val):
    """Returns if has prefix , the prefix (detected) and cleaned version"""
    
    if not val:
        return False, None, None
    val_s = val.split(' ')
    if len(val_s) <=1:
        return False, None, val.upper()
    
    val = val.lower()
    prefix = get_prefix(val)
    if len(prefix) > 0:
        return True, str(prefix.upper()), str(val.replace(prefix,'').upper())

    return False, None, val.upper()

def get_prefix(val):
    prefix_list = ['m ', 'm. ', 'mme ', 'dh ', 'm mme ', 'm. mme ', 
    'm. et mme ', 'm et mme ', 'mr ', 'miss ', 'ms ', 'm.mme ', 
    'mrs ', 'mr & ms ','mlle ']

    # DH MW??
    prefix_list.sort(key = lambda s: -len(s))

    for s in prefix_list:
        if val.find(s) == 0:
            return s
    return ''

def split_name(val):
    if not val:
        return None, None ,None, None
    
    val_s = val.split(' ')
    if len(val_s) == 1:
        return val, None, None, None
    if len(val_s) == 2:
        return val_s[0], val_s[1], None, None
    else:
        val_suspect = None
        if len(val_s[0]) < 4:
            val_suspect = val_s[0]
        if val_s[0].upper() =='MLLE':
            val_suspect = val_s[0]
            print("found mlle")
        return  val_s[0], val_s[1], " ".join(val_s[2:]), val_suspect