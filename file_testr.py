"""
File for testing new files and custom approaches - remove it when all will be clear

"""
import pandas as pd
from pandas.io.json import json_normalize
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
from glob import glob

from enum import Enum

class ProductFiles(Enum):
    ACCOUNT = 'account'
    CUSTOMER = 'customer'


pd.set_option('mode.chained_assignment', None)

@elapsedtime
def save_xlsx(target=ProductFiles.CUSTOMER):
    df = None
    if target == ProductFiles.CUSTOMER:
        df = cst.read_customer_file()
    elif target == ProductFiles.ACCOUNT:
        df = acc.read_accounts_file()
    else:
        print('Invalid argument - target')
        return
    print(df.shape)
    print(df.columns)
    f_name = f"./output/{target}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.xlsx"
    # df.to_excel(f_name, index = None, header=True)

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
def valid_birthday_tax(df):
    """ valid birthday with TAX.ID """
    
    # df = cst.read_customer_file()

    # very old people
    # print(df.sort_values(['DATE.OF.BIRTH'])['DATE.OF.BIRTH'].query('DATE.OF.BIRTH < 19200000'))
    
    df['VALID_BIRTH'] = (df['DOMICILE']+'|'+df['TAX.ID']+'|'+df['DATE.OF.BIRTH']).astype(str).map(vld.validate_birthday)
    df['VALID_EMAIL'] = df['EMAIL.1'].map(vld.valid_email)
    
    f_name = f"./output/birth_tax.id_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.xlsx"
    df[['CUSTOMER.CODE','DOMICILE','DATE.OF.BIRTH','TAX.ID','VALID_BIRTH','EMAIL.1','VALID_EMAIL','PHONE.1','SMS.1']].to_excel(f_name, index = None, header=True)


def too_many_tylda(val):
    if val == None:
        return '0'
    
    return '1' if len(val.split('~')) > 2 else '0'

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
    print('Duplicated customers num:', len(df_s))

    df['TYLDA_PROBLEM'] = df['REGROUPE'].astype(str).map(too_many_tylda)

    df['RATACHE_PROBLEM'] = df.apply(lambda x: '1' if pd.notnull(x['REGROUPE']) and pd.notnull(x['IS.RELATION.TYPE']) else '0', axis=1)


    # f_name = f'duplicated_acc.id_{date.today().isoformat()}.xlsx'
    # df_s[['CUSTOMER','ACCOUNT', 'CATEGORY', 'CURRENCY']].to_excel(f_name, index = None, header=True)

    # f_name = f'tylda_acc_{date.today().isoformat()}.xlsx'
    # df.query("TYLDA_PROBLEM == '1'")[['CUSTOMER','ACCOUNT', 'REGROUPE']].to_excel(f_name, index = None, header=True)

    # f_name = f'ratache_acc_{date.today().isoformat()}.xlsx'
    # df.query("RATACHE_PROBLEM == '1'")[['CUSTOMER','ACCOUNT', 'REGROUPE', 'IS.RELATION.OF']].to_excel(f_name, index = None, header=True)



    # df_reg = df['REGROUPE'].str.split('~',expand=True)
    # df_rat = df['IS.RELATION.OF'].str.split('|',expand=True)
    # print(df_reg.rename(columns=lambda x: 'REGROUPE_'+str(x)).head())
    # print(df_rat.rename(columns=lambda x: 'IS.RELATION.OF_'+str(x)).head())
    


@elapsedtime
def incorrect_email_address():
    
    # migration-first-ver
    df = cst.read_customer_file()
    # emails only in retail schema
    df = df.query('SECTOR < 1007 | SECTOR == 1901')

    df['VALID_EMAIL'] = df['EMAIL.1'].map(vld.valid_email)
    
    # df.query('VALID_EMAIL == 0')[['CUSTOMER.CODE', 'EMAIL.1']].to_excel('wrong-empty-emails.xlsx', index = None, header=True)
    df_bad_emails = df.query('VALID_EMAIL == 0')[['CUSTOMER.CODE', 'EMAIL.1','PHONE.1','SMS.1','NAME.1', 'NAME.2', 'ADDRESS']]

    df_acc = acc.read_accounts_file()

    df_m = pd.merge(df_acc, df_bad_emails, left_on='CUSTOMER', right_on='CUSTOMER.CODE')
    df_m = df_m[['CUSTOMER', 'ACCOUNT','PHONE.1', 'SMS.1', 'NAME.1', 'NAME.2', 'ADDRESS', 'EMAIL.1']]
    df_m.to_excel('accounts_wrong_email.xlsx',index = None, header=True)

@elapsedtime
def combine_customer_account():
    df_cst = cst.read_customer_file()
    df_acc = acc.read_accounts_file()
    


    # df_merged = pd.merge(df_acc, df_cst, left_on='CUSTOMER', right_on='CUSTOMER.CODE')
    df_merged = df_acc[~df_acc['CUSTOMER'].isin(df_cst['CUSTOMER.CODE'])]
    print('Shape is:', df_merged.shape)
    
    f_name = f"./output/acc_cust_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
    df_merged.to_csv(f_name, index = None, header=True)
    
    df_merged['IS_RETAIL'] = df_merged['SECTOR.CU.NATCLI']
    retail = 'RE'
    sme = ['BA','CO', 'ET', 'OR']
    print('RETAIL',df_merged.query("IS_RETAIL == @retail").shape)

    print('EMPTY TAX_ID = ')
    
    # valid_birthday_tax(df_merged.query("IS_RETAIL == @retail"))

    print('SME', df_merged.query("IS_RETAIL in @sme").shape)

    #required_columns = ['CUSTOMER','ACCOUNT']
    # df_merged = df_merged[required_columns]

def combain_regroupe():
    df_cst = cst.read_customer_file()
    df_cst['CUSTOMER.CODE'] = df_cst['CUSTOMER.CODE'].astype(str)
    df_acc = acc.read_accounts_file()
    
    df_acc = df_acc[df_acc['REGROUPE'].notnull()]
    
    df_acc['CUSTOMER'] = df_acc['CUSTOMER'].astype(str)

    
    df_reg = df_acc['REGROUPE'].str.split('~',expand=True)
    df_rat = df_acc['IS.RELATION.OF'].str.split('|',expand=True)
    print(df_reg.rename(columns=lambda x: 'REGROUPE_'+str(x)).head(10))
    print(df_rat.rename(columns=lambda x: 'IS.RELATION.OF_'+str(x)).head(10))
    
    df_reg = df_reg.rename(columns=lambda x: 'REGROUPE_'+str(x))

    print(df_acc.shape)
    df_acc = pd.concat([df_reg,df_acc], axis=1).reindex(df_reg.index)
    print(df_acc.shape)
    
    df_merged = pd.merge(df_acc, df_cst, left_on='REGROUPE_1', right_on='CUSTOMER.CODE', how='outer', indicator=True)
    # left_merged = 'both' #left_only
    left_merged = 'left_only'
    df_regr1 = df_merged.query('_merge == @left_merged')[['ACCOUNT', 'CUSTOMER.CODE','REGROUPE']].reset_index(drop=True)
    print(df_regr1.shape, df_regr1)

    

@elapsedtime
def read_databe_files():
    
    from glob import glob

    databe_files = sorted(glob('./databe/dane*.json'))
    databe_data = {}
    for f in databe_files:
        with open(f) as json_file:
            data = json.load(json_file)
            databe_data[data['identifier']] = data
    
    # print(json.dumps(databe_data['BE0865574649'],indent=4))

if __name__ == "__main__":
    print(f"File tester - start{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}")
    # sector()

    # dictionary_producer('account', 'L.AC.TYPE')
    accounts()
    combain_regroupe()
    # save_xlsx(ProductFiles.ACCOUNT)
    # incorrect_email_address()

    # combine_customer_account()
    # read_databe_files()

    print('File tester - end')