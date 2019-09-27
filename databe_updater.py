
import json
from glob import glob
from util_func import elapsedtime

@elapsedtime
def get_databe_data():

    databe_files = sorted(glob('./databe/dane*.json'))
    databe_data = {}
    for f in databe_files:
        with open(f) as json_file:
            data = json.load(json_file)
            databe_data[data['identifier']] = data
    
    return databe_data

DATABE_DATA = get_databe_data()

###### util funcs
def get_not_nested_data(val, name):
    val = val.split('|')
    if len(val) == 1:
        return None
    return DATABE_DATA[val[0]][name] if val[0] in DATABE_DATA.keys() else val[1]

def get_in_array_zero(val, array, name):
    val = val.split('|')
    if len(val) == 1:
        return None
    
    if val[0] not in DATABE_DATA.keys():
        return val[1]
    if len(DATABE_DATA[val[0]][array]) == 0:
        return val[1]
    return DATABE_DATA[val[0]][array][0][name]

###### fields  #######################

def city(val):
    return get_in_array_zero(val,'addresses','municipality')
    
def street_name(val): 
    return get_in_array_zero(val,'addresses','street')

def postal(val):
    return get_in_array_zero(val,'addresses', 'zip_code')

def street_number(val):
    return get_in_array_zero(val,'addresses' 'house_number')


def company_name(val):
    return get_not_nested_data(val,'company_name')

def company_vat_number(val):
    return get_not_nested_data(val,'vat_clean')
        
def company_start_date(val):
    return get_not_nested_data(val, 'start_date')

def company_registered_number(val):
    return get_not_nested_data(val, 'vat_clean')

