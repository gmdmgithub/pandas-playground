"""
functions for data conversion in dataframes

"""
from datetime import datetime
import phonenumbers as phn
import re
import validators_util as vld
import faker_producer as fp
import dictionary_mapper as dm
import util_func as ut

import pandas as pd

from customers import IS_TEST_ENVIRONMENT, DEFAULT_MAIL, DEFAULT_PHONE, DEFAULT_PHONE_PREFIX


def to_lowercase(val):
    """
    simply converts val to lower case - change object to str

    Arguments -- val: single cell
    Return: converted to str lowercase cell
    """
    if ut.isnull(val):
        return None
    val = str(val)
    return val.lower()


def float_converter(val):
    """
    converts value from cell to float

    Arguments -- val: single cell
    Return: float value of cell or none
    """
    if ut.isnull(val):
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

    Sample addresses to test
    # 91 WATERLOO ROAD
    # RUE NEUVE 82
    # RUE FELIX DELHASSE 14 /TM
    # GRNAD-ROUTE  22A/9
    # AV DE 14 JUILLET  41
    # AVENUE DES CITRONNIERS 57 BTE 3
    # RES. LE 205  RUE GRANDE 205/1.3
    # VIA SETTI CARRARO 15/F
    # VIA NICOLA SCARANO 3 INT3
    """
    if ut.isnull(val):
        return None, None, None

    house = None
    apartment = None

    # remove more than two spaces
    val = re.sub("[  ]{2,}", " ", val).strip()

    # BTE - flat number
    val = re.sub(" BTE[^a-zA-Z]", "/", val)
    val = re.sub(" BTE ", "/", val)
    if len(re.findall(r"[0-9]{1,}BTE[^a-zA-Z]", val)) > 0:
        repl_str = re.findall(r"[0-9]{1,}BTE", val)[-1]
        val = val.replace(repl_str, repl_str.replace('BTE', "/"))

    # remove spaces before and after house-apartment devider
    val = re.sub(" /", "/", val)
    val = re.sub("/ ", "/", val)

    # split the address
    street = val
    addr = val.split(' ')

    # just one no case
    if len(addr) == 1:
        return (fp.street_name(val), house, apartment) if IS_TEST_ENVIRONMENT else (val, house, apartment)

    # most common cases - last contain a number
    if re.search(r"[0-9]{1,}", addr[-1]) and len(re.search(r"[0-9]{1,}", addr[-1]).group()) > 0:
        street = ' '.join(addr[:-1])
        house = addr[-1]
        splitted = addr[-1].split('/')
        if len(splitted) > 1:
            house = splitted[0]
            apartment = splitted[1]

    return (fp.street_name(val), fp.street_number(val), apartment) if IS_TEST_ENVIRONMENT else (val, house, apartment)


def date_converter(val):
    """
    converts date from R11 files in format YYYYMMDD to YYYY-MM-DD

    Arguments -- val: single cell
    Return: iso date as expected in API
    """
    if ut.isnull(val):
        return None

    # simpler approach
    # return f'{val[0:4]}-{val[4:6]}-{val[-2:]}'
    try:
        # this approach required date to be valied
        return datetime.strptime(val, '%Y%m%d').date().isoformat()
    except:
        # TODO??? to be decided case with invalid date
        return None


def pep(val):
    """
    Convert pep value from origin Service "N", "Y", None to Boolean

    Arguments -- val: single cell
    Return: converted value #Tomasz Mierzwiński decission False as default
    """
    if ut.isnull(val):
        return False
    return True if val == 'Y' else False


def phone_segmenter(val):
    """
    Function converts phone number into "semantic" valied, prefix, phone number, if possible

    Arguments -- val: single cell
    Return: 
    - True/False - if sematic is correct (corret digits number)
    - prefix - eg 48
    - phone number without prefix
    - True/False - phone possible - for the country
    """
    if ut.isnull(val):
        return False, DEFAULT_PHONE_PREFIX, DEFAULT_PHONE, False
    
    if str(val).find(DEFAULT_PHONE) > -1:
            return False, DEFAULT_PHONE_PREFIX, DEFAULT_PHONE, False
    try:
        num = phn.parse('+'+val, None)
        return True, str(num.country_code), str(num.national_number), phn.is_possible_number(num)
    except:
        return False, DEFAULT_PHONE_PREFIX, DEFAULT_PHONE, False


def combine_phone_numbers(sms, desk_phone):
    """
    Function combine phone number from SMS.1 and PHONE.1 and returns cleaned phoned if any is valied 
    First SMS as potential GSM number

    Arguments 
        -- sms - is SMS.1 from customer
        -- desk_phone - is PHONE.1 from customer
    Return: cleaned_phone
    """
    # Tomasz Motyl decision 03.10.2019:  for empty phone and SMS number 32 111 111 111

    
    if IS_TEST_ENVIRONMENT:
        return fp.phone_number(sms, desk_phone)
    phone = cln.phone_cleaner(sms)
    if phone:
        return phone
    desk_p = cln.phone_cleaner(desk_phone)
    return desk_p if desk_p else DEFAULT_PHONE


def us_person(residence, nationality):
    """
    Function to check if person is US person (taxes) 
    Arguments 
        -- residence - is SMS.1 from customer
        -- nationality - is PHONE.1 from customer
    Return: true/false
    """
    if ut.isnull(residence) and ut.isnull(nationality):
        return False
    return (residence == 'US' or nationality == 'US')


def email(email, prospect_id):

    return DEFAULT_MAIL.replace('[placeholder]',str(prospect_id)) if vld.valid_email(email) == 0 else email
    # Ł. Kźnia asked to change to empty string
    # return '' if vld.valid_email(email) == 0 else email


def identity_documents_array(id, country_code, doc_dict):
    """
    Function collect identity_documents for the customer 
    Arguments 
        -- id - customer id in T24
        -- country_code - code of the country of customer
        -- doc_dict - dictionary of all documents for the clients - Khalid file
    Return: array fo identity_documents required in HiLo schema (vds)
    """
    client_docs = [doc_dict[key]
                   for key in doc_dict.keys() if str(key[0]) == id]
    ret_array = []
    for client_doc in client_docs:
        doc_id = fp.document_id(client_doc['LEGAL.ID']) if IS_TEST_ENVIRONMENT else client_doc['LEGAL.ID']
        doc = {'document_type': dm.document_type(client_doc['LEGAL.DOC.NAME']),
               'document_id': doc_id,
               'expiration_date': date_converter(client_doc['LEGAL.EXP.DATE']),
               'issue_date': date_converter(client_doc['LEGAL.ISS.DATE']),
               'country_code': country_code
               }
        ret_array.append(doc)

    return ret_array

def identity_documents_array_splitted(country_code, id, doc_types, doc_ids, doc_issue_dates, doc_expiration_dates, for_id_first=False):
    """
    Function collect identity_documents for the customer 
    Arguments 
        -- id - customer id in T24
        -- country_code - code of the country of customer
        -- doc_dict - dictionary of all documents for the clients - Khalid file
    Return: array fo identity_documents required in HiLo schema (vds)
    """

    if len(doc_types.split('|')) != len(doc_ids.split('|')) != len(doc_issue_dates.split('|')) !=  len(doc_expiration_dates.split('|')):
        print(f'Problem{id}')

    ret_array = []
    for (doc_type,doc_id,doc_issue_date, doc_expiration_date)  in zip(doc_types.split('|'), doc_ids.split('|'), doc_issue_dates.split('|'), doc_expiration_dates.split('|')):
        
        doc_id = fp.document_id(doc_id) if IS_TEST_ENVIRONMENT else doc_id
        
        doc = {'document_type': dm.document_type(doc_type),
               'document_id': doc_id,
               'expiration_date': date_converter(doc_expiration_date),
               'issue_date': date_converter(doc_issue_date),
               'country_code': country_code
               }
        ret_array.append(doc)

    if for_id_first:
        for ret_val in ret_array:
            if ret_val['document_id'] and len(ret_val['document_id']) > 0:
                return 'data exist - fake value', ret_val['document_type'], ret_val['expiration_date']
        return None, None, None

    return ret_array



# TODO FINALLY TO REMOVE
if __name__ == "__main__":
    print(street_converter('RES. LE 205  RUE GRANDE 205/1.3'))
