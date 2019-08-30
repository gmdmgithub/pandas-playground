


def to_lowercase(val):
    if not val:
        return None    
    try:
        return val.lower()
    except:        
        return val

def float_converter(val):
    if not val:
        return None    
    try:
        return np.float(val.replace(' ','').replace(',','.'))
    except:        
        return 'B'
