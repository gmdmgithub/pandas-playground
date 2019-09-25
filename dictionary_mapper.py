"""
functions for conversion dictionaries between two systems

"""
import dictionary_mapper_switcher as dms

def convert(val, switcher, default_val=None):
    """
    main function, converts value from cell (dictionary from source system) to target system dict val
    
    Arguments 
    -- val: single cell dict value (source system)
    -- switcher - converter for the dictionary
    -- default_val - default value if not matched or val is None
    Return: matched dictionary value for target system
    """
    if not val:
        return default_val
    return switcher.get(val) if switcher.get(val) else default_val

def document_type(val):
    """convert LEGAL.DOC.NAME to document_type dict"""
    
    # TODO!! - default value?
    default_val = val

    # TODO!! - matching is essential
    switcher = {
        '9999': "PASSPORT"
    }
    return convert(val, switcher, default_val)

def segment_id(val):
    """convert dict TARGET to customer_segment_id"""

    # TODO!! - default value?
    default_val = None

    # TODO!! - matching is essential
    switcher = {
        '9999': "PERSONAL",
        '9998': "BBB",
        '102': "CCC",
        '6': 'DDD',
        '101': 'DDD',
        '103': 'DDD',
        '104': 'DDD',
        '2': 'DDD',
        '1': 'DDD'
    }
    return convert(val, switcher, default_val)


def title(val):
    """convert dict TITLE to title"""

    # TODO!! - default value?
    default_val = None

    # TODO!! - matching is essential
    switcher = {
        'Mme': "AAA",
        'M': "BBB",
        'M.Mme': "CCC",
        'Mlle': 'DDD',
        'MM': 'DDD',
        'Mmes': 'DDD',
        'Mlles': 'DDD'
    }
    return convert(val, switcher, default_val)


def customer_status(val):
    """
    convert CUSTOMER.STATUS to customer_status
    customer_status ['ACTIVE','DORMANT','CLOSED']
    
    """
    # TODO!! - default value?
    default_val = 'ACTIVE'

    # TODO!! - matching is essential
    switcher = {
        '1': 'AAA',
        '1000': 'AAA',
        '1001': 'AAA',
        '3011': 'AAA',
        '3001': 'AAA',
        '3012': 'AAA',
        '3013': 'AAA',
        '3014': 'AAA',
        '3003': 'AAA',
        '3004': 'AAA',
        '3006': 'AAA',
        '23': 'AAA',
        '3015': 'AAA',
        '3008': 'AAA',
        '3009': 'AAA',
        '3005': 'AAA',
        '3010': 'AAA',
        '3007': 'AAA'
    }
    # TODO!!! wrong dict from R11
    return convert(val, switcher, default_val)

def display_lang(val):
    """convert dict LANGUAGE to display_and_messaging_language"""

    # TODO!! - default value?
    default_val = 'EN'

    # TODO!! - matching is essential
    switcher = {
        '1': "FR",
        '2': "NL",# Dutch
        '3': "EN",
        '4': 'FR' #'IT' #Italy
    }
    return convert(val, switcher, default_val)

def document_type(val):
    """convert dict LEGAL.DOC.NAME to document_type"""
    # TODO!! - default value?
    default_val = 'ID'

    # TODO!! - matching is essential
    switcher = {
        'CI.BELGE':'ID',
        'DOC.ID.MIG':'RESIDENCE_CARD',
        'CI.ETR':'RESIDENCE_CARD',
        'PASSEPORT':'PASSPORT',
        'SEJOUR':'RESIDENCE_CARD',
        'CI.SPEC':'RESIDENCE_CARD',
        'CI.TEMP':'RESIDENCE_CARD',
        'STATUT':'RESIDENCE_CARD',
        'ETRANGER':'RESIDENCE_CARD',
        'ADRESSE':'RESIDENCE_CARD'
    }

    return convert(val, switcher, default_val)


def residence_mapper(val):
    """convert dict RESIDENCE to residence"""
    
    # TODO!! - default value?
    default_val = False

    # TODO!! - matching is essential
    switcher = {
        'BE':True
    }

    return convert(val, switcher, default_val)

def us_person(val):
    """basis on dict RESIDENCE change to us_person dict"""
    default_val = False
    switcher = {
        "US": True
    }
    
    return convert(val, switcher, default_val)


def company_legal_form(val):
    """convert dict L.CU.FORM.JUR to company_legal_form"""
    default_val = val
    
    # Long switcher in dictionary_mapper_switcher file
    switcher = dms.company_legal_form_switcher
    
    return convert(val, switcher, default_val)
    

def company_nace_basic(val):
    """convert dict INDUSTRY to company_nace"""
    default_val = val
    
    # Long switcher in dictionary_mapper_switcher file
    switcher = dms.company_nace_basic_switcher
    
    return convert(val, switcher, default_val)

def product_type_id(val):
    """convert CATEGORY - accounts to product_type_id dict"""
    
    # TODO!! - default value?
    default_val = val

    # TODO!! - matching is essential
    switcher = {
        '1001':'VOD_1001',
        '1002':'VOD_1002',
        '1003':'VOD_1003',
        '1004':'VOD_1004',
        '1005':'VOD_1005',
        '1006':'VOD_1006',
        '1501':'VOD_1501'
    }
    return convert(val, switcher, default_val)
    