import pandas as pd
import numpy as np

import cleaners as cln
import validators_util as vld
import converters as cnv
import faker_producer as fp
import dictionary_mapper as dm
import databe_updater as dbu

import util_func as ut
from util_func import elapsedtime

import accounts as acc
import customers as cst

from time import process_time
from datetime import date, time, datetime
import json
import re


pd.set_option('mode.chained_assignment', None)

# TODO - move to config
IS_TEST_ENVIRONMENT = True
DEFAULT_MAIL = 'migration.[placeholder]@vodeno.com'
DEFAULT_PHONE = '111111111'
DEFAULT_PHONE_PREFIX = '32'
TEST_PROBE = 20000


@elapsedtime
def read_customer_file():
    """Read the CSV file with customer data"""

    # to optimize read only necessary columns
    use_columns = ['MARITAL.STATUS', 'TARGET', 'CUSTOMER.STATUS']
    types = {
        'MARITAL.STATUS': str,
        'TARGET': str,
        'CUSTOMER.STATUS': str,
        'DATE.OF.BIRTH': str,
        'LEGAL.EXP.DATE': str,
        'LANGUAGE': str,
        'CUSTOMER.CODE': str,
        'TAX.ID': str,
        'LEGAL.ID': str,
        'CALC.RISK.CLASS': str,
        'L.CU.FORM.JUR': str,
        'LEGAL.DOC.NAME': str,
        'SMS.1': str,
        'PHONE.1': str,
        'LEGAL.ISS.DATE': str
    }

    common_converters = {
        # 'SMS1':phone_cleaner, # coverts in-place - we want to have the original value
        'EMAIL.1': cnv.to_lowercase
    }

    nan_val = {
        "SMS.1": ['1', 'nan', '|', '0'],
        "PHONE.1": ['1', 'nan', '|', '0'],
    }

    encoding = 'UTF-8'
    f_name = './data/CUSTOMER-2019-10-03-01.CSV'

    df = pd.read_csv(f_name, sep=';',
                     encoding=encoding, decimal=',',
                     thousands=' ',
                     dtype=types,
                     na_values=nan_val,
                     # usecols=use_columns,
                     converters=common_converters,
                     error_bad_lines=False)

    ut.log_dataset_data(df)
    # TODO think over if not apply
    # df.replace('', np.nan, inplace=True)
    return df


@elapsedtime
def convert_retail_to_json():
    """
    Function read retail customer and produce json payload

    """

    df = read_customer_file()
    # ########################## print statistic - get only RETAIL CUSTOMERS

    df = df.query('SECTOR < 1007 | SECTOR == 1901')

    # second take only those with active accounts
    df_acc = acc.read_accounts_file('RETAIL')
    
    ut.log_dataset_data(df_acc)
    df_acc = df_acc.drop_duplicates(['CUSTOMER'], keep='first')
    ut.log_dataset_data(df_acc)
    
    # df_acc = df_acc[df_acc['REGROUPE'].isnull()]
    
    df_acc['CUSTOMER'] = df_acc['CUSTOMER'].astype(str)
    ut.log_dataset_data(df_acc)

    # .drop('CUSTOMER', axis=1, inplace=True)
    acc_columns = ['CUSTOMER','REGROUPE_0', 'REGROUPE_1','REGROUPE_2']
    df_basic = pd.merge(df, df_acc[acc_columns],
                  left_on='CUSTOMER.CODE', right_on='CUSTOMER')
    ut.log_dataset_data(df_basic)
    df_regr_0 = pd.merge(df, df_acc[acc_columns],
                  left_on='CUSTOMER.CODE', right_on='REGROUPE_0')
    ut.log_dataset_data(df_regr_0)

    df_regr_1 = pd.merge(df, df_acc[acc_columns],
                  left_on='CUSTOMER.CODE', right_on='REGROUPE_1')
    ut.log_dataset_data(df_regr_1)

    df_regr_2 = pd.merge(df, df_acc[acc_columns],
                  left_on='CUSTOMER.CODE', right_on='REGROUPE_2')
    ut.log_dataset_data(df_regr_2)
    
    df = pd.concat([df_basic, df_regr_0, df_regr_1,df_regr_2])
    ut.log_dataset_data(df)
    
    df = df.drop_duplicates(['CUSTOMER.CODE'], keep='first')
    ut.log_dataset_data(df)

    if IS_TEST_ENVIRONMENT:
        df = df.head(TEST_PROBE)
        ut.log_dataset_data(df)

    # ##########################rename columns which does not need to be converted
    df.rename(columns={'GENDER': 'sex', 'NATIONALITY':
                       'nationality', 'DOMICILE': 'country_code',
                       'CUSTOMER.CODE': 'prospect_id'}, inplace=True)
    df = df.reset_index()
    # ################ CONVERTION MAPPING STARTS ########
    
    # After discussion with business
    df['country_code'] = df['RESIDENCE']

    if IS_TEST_ENVIRONMENT:
        df['first_name'] = df['sex'].map(fp.first_name)
        df['last_name'] = df['FAMILY.NAME'].map(fp.last_name)
        df['national_register_number'] = df['TAX.ID'].map(
            fp.national_register_number)
    else:
        df['first_name'] = df['GIVEN.NAMES']
        df['last_name'] = df['FAMILY.NAME']
        
        # TODO ! Waiting for final decision - what to do if tax.id is empty
        df['national_register_number'] = df['TAX.ID']

    df['full_name'] = (df['first_name'] + ' ' + df['last_name']).astype(str)

    # DONE - Decision Jan Grybos Retail - 1001, SME 2001
    # df['customer_segment_id'] = df['TARGET'].map(dm.segment_id)
    df['customer_segment_id'] = '1001'

    # First approach was taking from seperat file
    # from file_testr import get_leagal_doc_set
    # documents_dict = get_leagal_doc_set().to_dict(orient='index')
    # df['identity_documents'] = df.apply(lambda x:
    #                                     cnv.identity_documents_array(x['prospect_id'], 
    #                                         x['country_code'], documents_dict), axis=1)
    
    df['identity_documents'] = df.apply(lambda x:
                                        cnv.identity_documents_array_splitted( 
                                            x['country_code'], x['prospect_id'], str(x['LEGAL.DOC.NAME']),
                                            str(x['LEGAL.ID']),str(x['LEGAL.ISS.DATE']),str(x['LEGAL.EXP.DATE'])), axis=1)

    
    # ####tax_residence_main_country nested
    # Business - A.Bujalska decided that data is empty 02.10.2019
    df['tax_residence_main_country'] = df.apply(lambda x:
                                                {'date': "",
                                                 'tin': x['national_register_number'],
                                                 'country': x['RESIDENCE']}, axis=1)

    #business A.Bujalska decided that array is empty 02.10.2019
    df['tax_residence_other_countries'] = np.empty((len(df), 0)).tolist()

    
    ## residential_address - nested
    df['ra_street_name'],  df['ra_street_number'], df['ra_apartment'] = zip(
        *df['STREET'].map(cnv.street_converter))
    
    if IS_TEST_ENVIRONMENT:
        df['ra_city'] = df['TOWN.COUNTRY'].map(fp.city)
        df['ra_postal'] = df['POST.CODE'].map(fp.postalcode)
    else:
        df['ra_city'] = df['TOWN.COUNTRY']
        df['ra_postal'] = df['POST.CODE']
    
    df['ra_country'] = df['RESIDENCE']

    df['residential_address'] = df.apply(lambda x:
                                         {'street_name': x.ra_street_name,
                                          'street_number': x.ra_street_number,
                                          'apartment': x.ra_apartment,
                                          'city': x.ra_city,
                                          'postal': x.ra_postal,
                                          'country': x.ra_country}, axis=1)

    # mailing_address = residential_address
    df['mailing_address'] = df['residential_address']

    # phone_number  phone_number_prefix
    df['phone_number'] = df.apply(lambda x: cnv.combine_phone_numbers(x['SMS.1'], x['PHONE.1']), axis=1)

    # let's add country to the GSM
    df['CL_GSM_ADDED_PREFIX'] = (
        df['country_code'] + df['phone_number']).astype(str).map(cln.phone_prefix_updater)
    # grab more data from spoused to be valid gsm
    
    df['CL_GSM_VALID'], df['phone_number_prefix'], df['phone_number'], df['CL_GSM_POSSIBLE'] = zip(
        *df['CL_GSM_ADDED_PREFIX'].map(cnv.phone_segmenter))

    if IS_TEST_ENVIRONMENT:
        df['email_address'] = df.apply(lambda x: fp.email(
            x['EMAIL.1'], x['prospect_id']), axis=1)
        df['birth_place'] = df['L.CU.POB'].map(fp.city)
        df['birth_date'] = df['DATE.OF.BIRTH'].map(fp.date_of_birth)
    else:
        df['email_address'] = df.apply(lambda x: cnv.email(x['EMAIL.1'], x['prospect_id']), axis=1)
        df['birth_place'] = df['L.CU.POB']
        df['birth_date'] = df['DATE.OF.BIRTH'].map(cnv.date_converter)

    df['title'] = df['TITLE'].map(dm.title)
    df['us_person'] = df.apply(lambda x: cnv.us_person(
        x['RESIDENCE'], x['nationality']), axis=1)

    # Business decission: tax_residence_other_countries - nested - not exists 1.10.2019

    df['pep'] = df['L.CU.PEP'].map(cnv.pep)
    # Tomasz Mierzwinski - Confluence 03.10.2019
    df['customer_kyc_risk'] = df['CALC.RISK.CLASS'].map(dm.customer_kyc_risk)

    # TODO!! - field does not exits
    df["customer_role"] = "OWNER"

    df['marital_status_id'] = df['MARITAL.STATUS'].map(dm.marital_status_id)
    df['residence'] = df['RESIDENCE'].map(dm.residence_mapper)
    df['occupation'] = df['EMPLOYMENT.STATUS'].map(dm.occupation)

    df['rooted'] = False
    # mapping add [2, 3, 1, 4] 1 FR, 2 NL, 3, EN, 4 IT
    df['display_and_messaging_language'] = df['LANGUAGE'].map(dm.display_lang)
    df['legal_language'] = df['display_and_messaging_language']

    # dictionary SRC.TO.BMPB - field added by Khalid 3.10.2019 - total number 86 records!
    df["source_of_funds"] = df['SRC.TO.BMPB'].map(dm.source_of_funds)
    
    # TODO! - dictionary to be mapped: L.CU.SRC.WEALTH - no data in customer
    df['source_of_wealth'] = "GAMBLING"

    df['normalized_email_address'] = df['email_address'].map(
        cln.normalize_email)

    # Tomasz Motyl decided - only ACTIVE clients are migrated
    # df['CUSTOMER.STATUS'].map(dm.customer_status)
    df['customer_status'] = 'ACTIVE'

    # fields after first tests
    df["pin_code_set"] = False
    df["face_id_set"] = False
    df["touch_id_set"] = False


    df['agreements'] = np.empty((len(df), 0)).tolist()
    df["consents"] = np.empty((len(df), 0)).tolist()

    # these fields will be no londer empty arrays
    # Flora Fred decided to have it all filed in
    df['agreements'] = df['agreements'].apply(lambda x: ut.agreements_producer('RETAIL'))
    df['consents'] = df['consents'].apply(lambda x: ut.consents_producer())
    
    columns = ['first_name', 'last_name', 'full_name', 'sex', 'national_register_number',
               'identity_documents',
            #    'document_type_list', # finally  it is identity_documents
               'customer_segment_id', 'nationality',
               'tax_residence_main_country',
               'tax_residence_other_countries',
               'residential_address',
               'mailing_address',
               'phone_number_prefix', 'phone_number', 'email_address', 'us_person',
               'birth_date', 'birth_place', 'pep', 'customer_kyc_risk', 'customer_role', 'residence', 'occupation', 'rooted',
               'pin_code_set', 'face_id_set', 'touch_id_set', 'agreements', 'consents',
               'source_of_funds', 'normalized_email_address', 'legal_language', 'display_and_messaging_language', 'source_of_wealth',
               'prospect_id'
               ]

   
    
    # request from Florentyna Frend
    # df['first_not_empty_doc_id'], df['first_not_empty_doc_type'], df['first_not_empty_doc_expiration']= zip(*df.apply(lambda x: cnv.identity_documents_array_splitted( 
    #                                         x['country_code'], x['prospect_id'], str(x['LEGAL.DOC.NAME']),
    #                                         str(x['LEGAL.ID']),str(x['LEGAL.ISS.DATE']),str(x['LEGAL.EXP.DATE']), True), axis=1))
    
    # df_flora = df[['national_register_number', 'prospect_id', 'country_code', 'first_not_empty_doc_id', 'first_not_empty_doc_type','first_not_empty_doc_expiration']]
    # df_flora['national_register_number'] = df_flora['national_register_number'].map(lambda x: None if (x is not None and len(str(x)) < 3) else x)
    # df_flora = df_flora[df_flora['national_register_number'].isnull()]
    # df_flora.to_excel('flora_tax_id.xlsx', index = None, header=True)

    res = df[columns].to_json(orient='records')
    res = json.loads(res)
    with open(ut.file_name('customer_retail'), 'w', encoding='UTF-8') as f:
        json.dump(res, f, indent=4)

    print(f'Num of customer no phones is: {fp.missed_phone_counter}')
    print(f'Num of customer no tax.id\'s is: {fp.missed_tax_id_counter}')
    print(f'Num of customer no emails is: {fp.missed_email_counter}')


@elapsedtime
def convert_sme_to_json():
    """
    Function read SME customer and produce json payload

    """
    start = process_time()
    df = read_customer_file()

    # ##########################rename columns which does not need to be converted
    df.rename(columns={'NAME.1': 'company_name', 'NATIONALITY': 'nationality',
                       'DOMICILE': 'country_code', 'POST.CODE': 'postalcode', 'RESIDENCE': 'country',
                       'CUSTOMER.CODE': 'prospect_id',
                       'TAX.ID': 'company_registered_number'}, inplace=True)

    # ########################## CONVERTION MAPPING STARTS
    df = df.query(
        'SECTOR > 1999 | SECTOR == 1501 | SECTOR == 1502 | SECTOR == 1602')
    # DONE - Decision Jan Grybos Retail - 1001, SME 2001
    # df['customer_segment_id'] = df['TARGET'].map(dm.segment_id)
    df['customer_segment_id'] = '2001'

    # fake name and street
    df['company_name'] = (df['company_registered_number'] +
                          '|'+df['company_name']).astype(str).map(dbu.company_name)
    df['fk_street_name'] = df['STREET'].map(fp.street_name)

    df['fk_street_number'] = df['STREET'].map(fp.street_number)
    df['fk_apartment'] = df['STREET'].map(fp.apartment)
    df['city'] = df['TOWN.COUNTRY'].map(fp.city)

    df['company_address'] = df.apply(lambda x:
                                     {'street_name': x.fk_street_name,
                                      'street_number': x.fk_street_number,
                                      'apartment': x.fk_apartment,
                                      'city': x.city,
                                      'postal': x.postalcode,
                                      'country': x.country_code}, axis=1)

    df['company_vat_number'] = df['company_registered_number']

    # mapping
    df['company_legal_form'] = df['L.CU.FORM.JUR'].map(dm.company_legal_form)
    # TODO!! - only 39 records with this date
    #df['company_start_date']= df['BIRTH.INCORP.DATE'].map(cnv.date_converter)
    df['company_start_date'] = df['company_registered_number'].map(
        fp.past_date)

    df['company_status'] = 'ACTIVE'
    # mapping

    df['company_nace_basic'] = df['INDUSTRY'].map(
        dm.company_nace_basic).astype(str)
    df['company_nace'] = df['company_nace_basic'].apply(lambda x: [x])

    # ####tax_residence_main_country nested
    # no date - fake added - must be different
    df['trmc_date'] = df['company_registered_number'].map(fp.past_date)
    df['trmc_tin'] = df['company_registered_number']
    df['trmc_country'] = df['country']

    df['tax_residence_main_country'] = df.apply(lambda x:
                                                {'date': x.trmc_date,
                                                 'tin': x.trmc_tin,
                                                 'country': x.trmc_country}, axis=1)
    # Business decided empty 01.10.2019
    df['tax_residence_other_countries'] = np.empty((len(df), 0)).tolist()

    df['us_person'] = df['country'].map(dm.us_person)
    df['is_migrated'] = True
    df['customer_status'] = 'ACTIVE'
    df['legal_language'] = df['LANGUAGE'].map(dm.display_lang)

    # TODO! - Tomasz Mierzwiński
    df['company_kyc_risk'] = '5'

    # todo!! - empty fields
    df['agreements'] = np.empty((len(df), 0)).tolist()

    columns = ['customer_segment_id', 'company_name',
               'company_address',
               'company_registered_number', 'company_vat_number', 'company_legal_form', 'company_start_date',
               'company_status', 'company_nace_basic', 'company_nace',
               'tax_residence_main_country',
               'tax_residence_other_countries',
               'us_person',
               'agreements',
               'company_kyc_risk',
               'is_migrated',
               'legal_language',
               'prospect_id'
               ]
    res = df[columns].to_json(orient='records')
    res = json.loads(res)
    with open(ut.file_name('customer_sme'), 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=4)


if __name__ == "__main__":
    convert_retail_to_json()
    # convert_sme_to_json()
