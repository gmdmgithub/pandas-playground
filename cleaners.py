import re


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


