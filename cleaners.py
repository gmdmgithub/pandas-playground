import re
import phonenumbers as phn

def phone_cleaner(val):
    if not val:
        return None
    try:
        #remove leading 0, ',' / \ .
        val = re.sub("e[+-]0.*", "", val).lstrip('0')
        val = re.sub("\D", "", val)
        #replace(',','').replace('/','').replace('\\','').replace('.','').replace('(','').replace(')','').replace('+','') 
        # to be decided
        # if len(val) < 6:
        if len(val) < 3: # many just 1, 2, ? or 65 -  eliminate
            val = None
        return val
    except:        
        return None

def get_country_phone_code(country_iso):
    if not country_iso:
        return None
    country_iso = str(country_iso)
    for code, iso in phn.COUNTRY_CODE_TO_REGION_CODE.items():
        if country_iso.upper() in iso:
            return str(code)
    return None

def phone_prefix_updater(val):
    """"updates country prefix on the phone"""
    
    if not val:
        return None
    # looking only for country prefix
    iso = re.sub('[^A-Za-z]', "", val)
    cleared_phone = re.sub(r"\D", "", val)

    country_code = get_country_phone_code(iso)
    if country_code is None:
        return cleared_phone
    
    # it means for sure country code in the scope of phone number
    if len(cleared_phone) > 8:
        if (val.find(country_code) + 1) == len(country_code):
            return cleared_phone 

    return country_code + cleared_phone

if __name__ == "__main__":
    print(phone_prefix_updater('UZ99890929921'))