"""
functions for data conversion in dataframes

"""
from datetime import datetime
import re

def to_lowercase(val):
    """
    simply converts val to lower case - change object to str
    
    Arguments -- val: single cell
    Return: converted to str lowercase cell
    """
    if not val:
        return None
    val = str(val)
    return val.lower()

def float_converter(val):
    """
    converts value from cell to float
    
    Arguments -- val: single cell
    Return: float value of cell or none
    """
    if not val:
        return None
    try:
        return np.float(val.replace(' ', '').replace(',', '.'))
    except:
        return None


def street_converter(val):
    """
    Function converts free-hand address into street name, house and flat no 
    
    Arguments -- val: single cell
    Return: street name, house no, flat no
    """
    if not val:
        return None
    # TODO! - split into 3 name, house and apartment, some samples below
    # 91 WATERLOO ROAD
    # RUE NEUVE 82
    # RUE FELIX DELHASSE 14 /TM
    # GRNAD-ROUTE  22A/9
    # AV DE 14 JUILLET  41
    # AVENUE DES CITRONNIERS 57 BTE 3
    # RES. LE 205  RUE GRANDE 205/1.3
    # VIA SETTI CARRARO 15/F
    # VIA NICOLA SCARANO 3 INT3

    house = None
    apartment = None
    
    #remove more than two spaces
    val = re.sub("[  ]{2,}", " ", val).strip()
    # remove spaces before and after house-apartment devider
    val = re.sub(" /", "/", val)
    val = re.sub("/ ", "/", val)

    #split the address
    street = val
    addr = val.split(' ')
    
    # just one no case
    if len(addr) == 1:
        return val, house, apartment
    
    # most common cases - last contain a number
    if re.search(r"[0-9]{1,}", addr[-1]) and len(re.search(r"[0-9]{1,}", addr[-1]).group()) > 0:
        street = ' '.join(addr[:-1])
        house = addr[-1]
        splitted = addr[-1].split('/')
        if len(splitted) > 1:
            house = splitted[0]
            apartment = splitted[1]

    
    return street, house, apartment

def date_converter(val):
    """
    converts date from R11 files in format YYYYMMDD to YYYY-MM-DD
    
    Arguments -- val: single cell
    Return: iso date as expected in API
    """
    if not val:
        return None

    # simpler approach
    # return f'{val[0:4]}-{val[4:6]}-{val[-2:]}'
    try:
        #this approach required date to be valied
        return datetime.strptime(val,'%Y%m%d').date().isoformat()
    except:
        #TODO??? discuse case with invalid date
        return None
    
def pep(val):
    """
    Convert pep value from origin Service "N", "Y", None to Boolean
    
    Arguments -- val: single cell
    Return: converted value
    """
    if not val:
        return None
    return True if val == 'Y' else False

if __name__ == "__main__":
    print(street_converter('RES. LE 205  RUE GRANDE 205/1.3'))