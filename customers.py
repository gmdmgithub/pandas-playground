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
TEST_PROBE = 1000


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
    f_name = './data/CUSTOMER-2019-09-26-01.CSV'

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
    df_acc = df_acc[df_acc['REGROUPE'].isnull()]
    df_acc['CUSTOMER'] = df_acc['CUSTOMER'].astype(str)
    ut.log_dataset_data(df_acc)

    # .drop('CUSTOMER', axis=1, inplace=True)
    df = pd.merge(df, df_acc['CUSTOMER'],
                  left_on='CUSTOMER.CODE', right_on='CUSTOMER')

    # df = df[df['SMS.1'].isnull()]
    # # check not matching customers
    # df = pd.merge(df,df_acc['CUSTOMER'], left_on='CUSTOMER.CODE', right_on='CUSTOMER', how='outer', indicator=True)
    # # left_merged = 'both' #left_only
    # left_merged = 'right_only'
    # df = df.query('_merge == @left_merged')[['CUSTOMER.CODE', 'CUSTOMER']].reset_index(drop=True)
    # print(df)

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

    df['country_code'] = df['RESIDENCE']

    # if IS_TEST_ENVIRONMENT:
    df['first_name'] = df['sex'].map(fp.first_name)
    df['last_name'] = df['FAMILY.NAME'].map(fp.last_name)
    df['full_name'] = (df['first_name'] + ' ' + df['last_name']).astype(str)

    df['national_register_number'] = df['TAX.ID'].map(
        fp.national_register_number)

    # TODO!! - problem with document | - separation
    df['document_type'] = df['LEGAL.DOC.NAME'].map(
        cln.document_type).map(dm.document_type)

    df['document_id'] = df['LEGAL.ID'].map(fp.document_id).astype(str)
    # TODO! proper date on migration
    df['expiration_date'] = df['LEGAL.EXP.DATE'].map(fp.future_date)
    # TODO! proper date on migration
    df['issue_date'] = df['LEGAL.ISS.DATE'].map(fp.past_date)
    # TODO!!! - LEGAL.ISS.AUTH - empty
    df['issuing_authority'] = 'Fake value'

    df['identity_documents'] = df.apply(lambda x:
                                        [{'document_type': x.document_type,
                                          'document_id': x.document_id,
                                          'expiration_date': x.expiration_date,
                                          'issue_date': x.issue_date,
                                          'issuing_authority': x.issuing_authority,
                                          'country_code': x.country_code
                                          }], axis=1)

    #  customer_segment_id - dictionary  #TARGET
    df['customer_segment_id'] = df['TARGET'].map(dm.segment_id)

    # building document type

    # todo test leagal doc
    from file_testr import get_leagal_doc_set
    documents_dict = get_leagal_doc_set().to_dict(orient='index')

    df['document_type_list'] = df.apply(lambda x:
                                        cnv.identity_documents_array(x['prospect_id'], x['country_code'], documents_dict), axis=1)

    # ####tax_residence_main_country nested
    df['trmc_date'] = df['TAX.ID'].map(fp.past_date)
    df['trmc_tin'] = df['national_register_number']
    df['trmc_country'] = df['RESIDENCE']

    df['tax_residence_main_country'] = df.apply(lambda x:
                                                {'date': x.trmc_date,
                                                 'tin': x.trmc_tin,
                                                 'country': x.trmc_country}, axis=1)

    # df['tax_residence_other_countries'] = df.apply(lambda x:
    #                                             [{'date': x.trmc_date,
    #                                              'tin': x.trmc_tin,
    #                                              'country': x.trmc_country}
    #                                              ], axis=1)

    # business - Flora and Agata decided that empty list should be sent
    df['tax_residence_other_countries'] = np.empty((len(df), 0)).tolist()

    ## residential_address - nested
    # first faker then have to be split from the street
    # df['ra_street_name'],  df['ra_street_number'], df['ra_apartment'] = zip(
    #     *df['STREET'].map(cnv.street_converter))
    df['ra_street_name'] = df['STREET'].map(fp.street_name)
    df['ra_street_number'] = df['STREET'].map(fp.street_number)
    df['ra_apartment'] = df['STREET'].map(fp.apartment)
    df['ra_city'] = df['TOWN.COUNTRY'].map(fp.city)
    df['ra_postal'] = df['POST.CODE'].map(fp.postalcode)

    # check if COUNTRY is string ? - its written LL.COUNTRY
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
    df['phone_number'] = df.apply(
        lambda x: fp.phone_number(x['SMS.1'], x['PHONE.1']), axis=1)
    # df['phone_number'] = df.apply(lambda x: cnv.combine_phone_numbers(x['SMS.1'], x['PHONE.1']), axis=1)

    # let's add country to the GSM
    df['CL_GSM_ADDED_PREFIX'] = (
        df['country_code'] + df['phone_number']).astype(str).map(cln.phone_prefix_updater)
    # grab more data from spoused to be valid gsm
    df['CL_GSM_VALID'], df['phone_number_prefix'], df['phone_number'], df['CL_GSM_POSSIBLE'] = zip(
        *df['CL_GSM_ADDED_PREFIX'].map(cnv.phone_segmenter))

    # TODO!! - convert and check - if empty put migration@vodeno.com
    df['email_address'] = df.apply(lambda x: fp.email(
        x['EMAIL.1'], x['prospect_id']), axis=1)
    # df['email_address'] = df.apply(lambda x: cnv.email(x['EMAIL.1'], x['prospect_id']), axis=1)

    df['title'] = df['TITLE'].map(dm.title)

    # TODO - how to migrate
    df['us_person'] = df.apply(lambda x: cnv.us_person(
        x['RESIDENCE'], x['nationality']), axis=1)

    # tax_residence_other_countries - nested - not exists

    # DATE.OF.BIRTH
    # TODO!! - convert and check
    df['birth_date'] = df['DATE.OF.BIRTH'].map(fp.date_of_birth)

    df['birth_place'] = df['L.CU.POB'].map(fp.city)
    df['pep'] = df['L.CU.PEP'].map(cnv.pep)

    # TODO Mapping
    df['customer_kyc_risk'] = df['CALC.RISK.CLASS']

    # TODO!! - field does not exits
    df["customer_role"] = "OWNER"

    df['marital_status_id'] = df['MARITAL.STATUS'].map(dm.marital_status_id)

    df['residence'] = df['RESIDENCE'].map(dm.residence_mapper)

    # Confirmation needed - Tomasz Mierzewinski decide to use EMPLOYMENT.STATUS,
    # OCCUPATION?? 3 values ['HEAD OF MISSION REP ARMENIE NATO', 'MILITAIRE', 'employé']
    df['occupation'] = df['EMPLOYMENT.STATUS'].map(dm.occupation)

    df['rooted'] = False
    # mapping add [2, 3, 1, 4] 1 FR, 2 NL, 3, EN, 4 IT
    df['display_and_messaging_language'] = df['LANGUAGE'].map(dm.display_lang)

    df['legal_language'] = df['display_and_messaging_language']

    # TODO!!! - no data SRC.TO.BMPB

    # df['source_of_funds'] = df['SRC.TO.BMPB']
    # TODO! - dictionary to be mapped:
    df["source_of_funds"] = "GAMBLING"
    # TODO! - dictionary to be mapped: L.CU.SRC.WEALTH - no data in customer
    df['source_of_wealth'] = "GAMBLING"

    df['normalized_email_address'] = df['email_address'].map(
        cln.normalize_email)

    # company???

    # TODO!!! - wrong dict from R11 - we migrate only active
    # df['CUSTOMER.STATUS'].map(dm.customer_status)
    df['customer_status'] = 'ACTIVE'

    # fields after first tests
    df["pin_code_set"] = False
    df["face_id_set"] = False
    df["touch_id_set"] = False

    df['agreements'] = np.empty((len(df), 0)).tolist()
    df["consents"] = np.empty((len(df), 0)).tolist()

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

    # simply save do json
    df[columns].to_json('test_c1.json', orient='records')

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

    df['customer_segment_id'] = "SME"

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

    df['tax_residence_other_countries'] = df.apply(lambda x:
                                                   [{'date': x.trmc_date,
                                                     'tin': x.trmc_tin,
                                                     'country': x.trmc_country}], axis=1)

    df['us_person'] = df['country'].map(dm.us_person)
    df['is_migrated'] = True
    df['customer_status'] = 'ACTIVE'
    df['legal_language'] = df['LANGUAGE'].map(dm.display_lang)

    # TODO! - what is the correct value
    df['company_kyc_risk'] = '5'

    # todo!! - empty fields
    df['agreements'] = np.empty((len(df), 0)).tolist()
    # df['tax_residence_other_countries'] = df['tax_residence_main_country']

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
