"""
File for testing new files and custom approaches - remove when project done

"""
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

@elapsedtime
def save_xlsx(target='customer'):
    df = None
    if target == 'customer':
        df = cst.read_customer_file()
    elif target == 'account':
        df = acc.read_accounts_file()
    else:
        print('Invalid argument - target')
        return

    f_name = f'{target}_{date.today().isoformat()}.xlsx'
    df.to_excel(f_name, index = None, header=True)

@elapsedtime
def sector():
    import chardet
    with open('./data/SECTOR.1909081335.MULTIVALUE.CSV', 'rb') as f:
        # print(f)
        result = chardet.detect(f.read())  # or readline if the file is large
        print('Chart detector', result['encoding'])

    # encoding = 'latin1'
    # encoding = 'ISO-8859-1'
    # encoding = 'cp1250'
    # encoding = 'UTF-8'
    # encoding = 'UTF-8'
    # encoding = 'ISO-8859-9'
    encoding = 'windows-1255'

    read_columns = ['Id', 'Fieldname', 'Value']

    df = pd.read_csv('./data/SECTOR.1909081335.MULTIVALUE.CSV', sep=';',
                     encoding=encoding, decimal=',', usecols=read_columns,  # reads only selected columns
                     thousands=' ', dtype=col_types)

    # logging.debug(df.info(memory_usage='deep'))
    print(df.tail(10))

    ut.log_dataset_data(df)

@elapsedtime
def dictionary_producer(target, dictionary):

    df = None
    if target == 'customer':
        df = cst.read_customer_file()
    elif target == 'account':
        df = acc.read_accounts_file()
    else:
        print('Invalid argument - target')
        return

    # print(df.shape)

    print(dictionary, df[dictionary].dropna().unique().tolist())

    # dict_list = df['LEGAL.DOC.NAME'].map(
    #     cln.document_type).dropna().unique().tolist()

    
    # print for dictionary
    dict_list = df[dictionary].dropna().unique().tolist()
    for x in dict_list:
        #     # if len(x.split('|')) > 2:
        #     #     print(x)
        print(f'\'{x}\':\'VOD_{x}\',')

@elapsedtime
def valid_birthday_tax():
    """ valid birthday with TAX.ID """
    
    df = cst.read_customer_file()

    # very old people
    # print(df.sort_values(['DATE.OF.BIRTH'])['DATE.OF.BIRTH'].query('DATE.OF.BIRTH < 19200000'))
    
    df['VALID_BIRTH'] = (df['DOMICILE']+'|'+df['TAX.ID']+'|'+df['DATE.OF.BIRTH']).astype(str).map(vld.validate_birthday)
    
    f_name = f'.\\data\\birth_tax.id_{date.today().isoformat()}.xlsx'
    df[['CUSTOMER.CODE','DOMICILE','DATE.OF.BIRTH','TAX.ID','VALID_BIRTH' ]].to_excel(f_name, index = None, header=True)

@elapsedtime
def accounts():

    df = acc.read_accounts_file()

    # print('COLUMN LIST',df.columns)

    print(df.CUSTOMER.count())
    print(len(df.CUSTOMER.unique().tolist()))
    
    # get only duplicated list
    #this way is cost effective
    # df_s = pd.concat(g for _, g in df.groupby("CUSTOMER") if len(g) > 1)
    customers = df["CUSTOMER"]
    df_s = df[customers.isin(customers[customers.duplicated()])].sort_values("CUSTOMER")

    print('Unique customers num:', len(df_s['CUSTOMER'].unique()))

    
    # f_name = f'duplicated_acc.id_{date.today().isoformat()}.xlsx'
    # df_s[['CUSTOMER','ACCOUNT', 'CATEGORY', 'CURRENCY']].to_excel(f_name, index = None, header=True)

def accounts_rel():
    df_a = acc.read_accounts_file()


if __name__ == "__main__":
    print('File tester - start')
    # sector()

    # dictionary_producer('account', 'L.AC.TYPE')
    # accounts()
    save_xlsx('customer')

    print('File tester - end')