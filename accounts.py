import pandas as pd
import numpy as np

import cleaners as cln
import validators_util as vld
import converters as cnv
import faker_producer as fp
import dictionary_mapper as dm

import util_func as ut
from util_func import elapsedtime

import accounts as acc
import customers as cst

from datetime import date, time, datetime
import json
import re

pd.set_option('mode.chained_assignment', None)

#TODO - move to config
IS_TEST_ENV = True


@elapsedtime
def read_accounts_file(type=None):
    """
    Read the CSV file with accounts data
    Arguments -- Type of customer realted to account if None - read all
    Return: dataframe with accounts

    """
    
    #TODO - when shape is known define to optimize
    use_columns = ['MARITAL.STATUS', 'TARGET','CUSTOMER.STATUS' ]
    
    types = {
        'ACCOUNT': str,
        'CATEGORY': str,
        'CURRENCY.MARKET': str,
        'ACCOUNT.OFFICER': str,
        'OTHER.OFFICER': str,
        'POSTING.RESTRICT': str,
        'OPENING.DATE': str,
        'OPEN.CATEGORY': str,
        'L.AC.PM.CO.EX': str,
        'L.AC.DATE.PR': str,
        'REGROUPE':str,
        'IS.RELATION.TYPE':str,
        'CUSTOMER':str
    }

    common_converters = {
        # 'SMS1':phone_cleaner, # coverts in-place - we want to have the original value
        'EMAIL': cnv.to_lowercase
    }
    
    encoding = 'utf-8'
    f_name = './data/BE0010001_ACCOUNT2.1909261440.csv'
    
    df = pd.read_csv(f_name, sep=';',
                     encoding=encoding, decimal=',',
                     thousands=' ',
                     dtype=types,
                    #  usecols=use_columns,
                    #  converters=common_converters,
                     error_bad_lines=False)
    

    if type == 'SME':
        df = df[df['SECTOR.CU.NATCLI'].isin(['BA', 'CO', 'ET', 'OR'])]
    elif type == 'RETAIL': 
        df = df[df['SECTOR.CU.NATCLI'].isin(['RE'])]
    
    return df

@elapsedtime
def prepare_json_for_accounts():
    
    df = read_accounts_file()
    
    # ########################## print statistic - get only RETAIL CUSTOMERS
    ut.log_dataset_data(df)
    if IS_TEST_ENV:
        df = df.head(100)
        ut.log_dataset_data(df)
    
    # ##########################rename columns which does not need to be converted
    df.rename(columns={'CURRENCY': 'currency', 'ACCOUNT.TITLE.1':
                       'internal_name', 'ALT.ACCT.ID': 'account_number',
                       'CATEGORY': 'product_type_id','CUSTOMER':'owner_id',
                        # 'SHORT.TITLE':'name', 
                        'POSTING.RESTRICT': 'status'}, 
                       inplace=True)

    # TODO?? Mapping from JOINT.HOLDER??
    df['co_ownership'] = 'INDIVIDUAL'
    #as a default
    df['status'] = 'ACTIVE'
    df['credit'] = df.apply(lambda x: {'amount': 0.0,
                                        'currency': x.currency
                                        }, axis=1)
    # k.benesrighe@tnaconsulting.net
    df['interest_rate'] = 0.0
    # df['information'] = 'MIGRATION'
    df['opening_date'] =df['OPENING.DATE'].map(cnv.date_converter)

    df['overdraft_flag'] = df['LINK.TO.LIMIT'].map(lambda x: x == 'YES')

    df['product_type_id'] = df['product_type_id'].map(dm.product_type_id)
    
    
    df['swift_bic_code'] = df['MNEMONIC']

    # TODO!!! field name is the name of the owner in the file
    df['name'] = 'MAIN ACCOUNT'

    columns = [
        'currency',
        #'internal_name',  # internal name is decided to be skipped
        'account_number', 'product_type_id', 
        # 'owner_id', #set in header
        'name', 
        'status', 'co_ownership', 'credit', 'interest_rate', 
        # 'information', #it is added in the tree
        'opening_date', 'overdraft_flag',
        'swift_bic_code'
    ]

    df = df[columns]

    res = df.to_json(orient='records')
    res = json.loads(res)
    with open(ut.file_name('current_accounts'), 'w', encoding='UTF-8') as f:
        json.dump(res, f, indent=4)


if __name__ == "__main__":
    prepare_json_for_accounts()