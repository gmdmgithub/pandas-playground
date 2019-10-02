"""
functions for conversion dictionaries between two systems

"""
import dictionary_mapper_switcher as dms
import util_func as ut
import pandas as pd

def convert(val, switcher, default_val=None):
    """
    main function, converts value from cell (dictionary from source system) to target system dict val
    
    Arguments 
    -- val: single cell dict value (source system)
    -- switcher - converter for the dictionary
    -- default_val - default value if not matched or val is None
    Return: matched dictionary value for target system
    """
    if ut.isnull(val):
        return default_val
    return switcher.get(val) if switcher.get(val) else default_val


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

    default_val = None

    # Accepted by business 02.10.2019 
    switcher = {
        'M': 'TITLE_MR',
        'M.Mme': 'TITLE_MS',
        'MM': 'TITLE_MRS',
        'Mlle': 'TITLE_MS',
        'Mlles': 'TITLE_MS',
        'Mme': 'TITLE_MRS',
        'Mmes': 'TITLE_MS'
    }
    return convert(val, switcher, default_val)


def customer_status(val):
    """
    convert CUSTOMER.STATUS to customer_status
    customer_status ['ACTIVE','DORMANT','CLOSED']
    
    """
    # decided always active
    default_val = 'ACTIVE'

    # TODO if change please provide
    switcher = {
        
    }
    return convert(val, switcher, default_val)

def display_lang(val):
    """convert dict LANGUAGE to display_and_messaging_language"""

    default_val = 'FR'

    # Accepted by business in September 2019 
    switcher = {
        '1': "FR",
        '2': "NL",# Dutch
        '3': "EN",
        '4': 'FR' #'IT' #Italy
    }
    return convert(val, switcher, default_val)

def document_type(val):
    """convert dict LEGAL.DOC.NAME to document_type"""
    default_val = None

    # Matching accepted by business 02.10.2019
    switcher = {
        'PASSEPORT': 'PASSPORT',
        'ADRESSE': 'RESIDENCE_CARD',
        'ADRESSE.FACT': 'MIGRATION_DOCUMENT_ID',
        'ADRESSE.TAX': 'MIGRATION_DOCUMENT_ID',
        'AUTOCERT': 'MIGRATION_DOCUMENT_ID',
        'AUTOCERT.PEP': 'MIGRATION_DOCUMENT_ID',
        'AYANT.DROIT': 'MIGRATION_DOCUMENT_ID',
        'AYANTDROIT': 'MIGRATION_DOCUMENT_ID',
        'CERT.MAR.PA': 'MIGRATION_DOCUMENT_ID',
        'CERT.NAISS': 'MIGRATION_DOCUMENT_ID',
        'CI.BELGE': 'ID',
        'CI.ETR': 'ID',
        'CI.KID': 'ID',
        'CI.SPEC': 'RESIDENCE_CARD',
        'CI.TEMP': 'RESIDENCE_CARD',
        'CONSTITUTION': 'MIGRATION_DOCUMENT_ID',
        'CONVENTION': 'MIGRATION_DOCUMENT_ID',
        'DECLNR': 'MIGRATION_DOCUMENT_ID',
        'DOC.ID.MIG': 'RESIDENCE_CARD',
        'ETRANGER': 'RESIDENCE_CARD',
        'EUR276': 'MIGRATION_DOCUMENT_ID',
        'HIS276': 'MIGRATION_DOCUMENT_ID',
        'PRESENTATION': 'MIGRATION_DOCUMENT_ID',
        'PROFESSION': 'MIGRATION_DOCUMENT_ID',
        'RGSTR.POPU': 'MIGRATION_DOCUMENT_ID',
        'SEJOUR': 'RESIDENCE_CARD',
        'STATUT': 'RESIDENCE_CARD'
    }

    return convert(val, switcher, default_val)


def residence_mapper(val):
    """convert dict RESIDENCE to residence"""
    
    default_val = False

    # Accepted by Tomasz Mierzwinski 1.10.2019
    switcher = {
        'BE':True
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

def occupation(val):
    """convert EMPLOYMENT.STATUS - accounts to occupation dict"""
    
    default_val = 'MIGRATION'

    # Accepted by business 02.10.2019
    switcher = {
        'AIDANT': 'UNEMPLOYED',
        'ETUDIANT': 'STUDENT',
        'FEMME.AU.FOYER': 'UNEMPLOYED',
        'FONCTIONNAIRE': 'PUBLIC_SERVANT',
        'FONCTIONNAIRECDD': 'PUBLIC_SERVANT',
        'INDEPENDANT': 'SELF_EMPLOYED',
        'NON.DEFINI': 'EMPLOYEE',
        'PENSIONNE': 'RETIREMENT',
        'PROFESSION.LIBERALE': 'SELF_EMPLOYED',
        'SALARIE.EMPLOYE': 'EMPLOYEE',
        'SALARIE.EMPLOYECDD': 'EMPLOYEE',
        'SALARIE.EMPLOYECDD2': 'EMPLOYEE',
        'SALARIE.EMPLOYECDI': 'EMPLOYEE',
        'SANS.EMPLOI': 'UNEMPLOYED',
        'STAGIAIRE': 'EMPLOYEE'
    }
    return convert(val, switcher, default_val)

def marital_status_id(val):
    """convert MARITAL.STATUS - accounts to marital_status_id dict"""
    
    default_val = None

    # Accepted by business 01.10.2019
    switcher = {
        '1': 'SINGLE',
        '2': 'MARRIED',
        '3': 'WIDO`WE`D',
        '4': 'DIVORCED',
        '5': 'SEPARATED',
        '6': 'SEPARATED',
        '7': 'LEGALLY_COHABITATING',
        '8': 'LEGALLY_COHABITATING'
    }
    return convert(val, switcher, default_val)

def source_of_wealth(val):
    """convert EB.LOOKUP.LOOKUP.NAME - to source_of_wealth"""
    
    default_val = None

    # TODO! - no dict from temenos
    switcher = {
        'AUTRE': 'PRIVATE_MEANS',
        'DONATION': 'INHERITANCE',
        'HERITAGE': 'INHERITANCE',
        'IMMOBILIER': 'PRIVATE_MEANS',
        'SALAIRE': 'WORK_SALARY',
        'VALEURSMOBILIERES': 'PRIVATE_MEANS',
    }
    return convert(val, switcher, default_val)

def source_of_funds(val):
    """convert EB.LOOKUP.LOOKUP.NAME - to source_of_funds"""
    
    default_val = None

    # TODO! - no dict from temenos
    switcher = {
        'AUTRE': 'PRIVATE_MEANS',
        'DONATION': 'INHERITANCE',
        'HERITAGE': 'INHERITANCE',
        'IMMOBILIER': 'PRIVATE_MEANS',
        'SALAIRE': 'WORK_SALARY',
        'VALEURSMOBILIERES': 'PRIVATE_MEANS',
    }
    return convert(val, switcher, default_val)