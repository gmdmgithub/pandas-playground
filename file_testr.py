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
    LEGAL_DOC = 'leagal_doc'


# k.benesrighe@tnaconsulting.net

pd.set_option('mode.chained_assignment', None)

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
    # print(df.columns)
    f_name = f"./output/{target}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.xlsx"
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
    if target == ProductFiles.CUSTOMER:
        df = cst.read_customer_file()
    elif target == ProductFiles.ACCOUNT:
        df = acc.read_accounts_file()
    elif target == ProductFiles.LEGAL_DOC:
        df = get_leagal_doc_set()
    else:
        print('Invalid argument - target')
        return

    # print(df.shape)

    print(dictionary, df[dictionary].dropna().unique().tolist())

    print(dictionary, len(df[dictionary].dropna().unique().tolist()))

    # dict_list = df['LEGAL.DOC.NAME'].map(
    #     cln.document_type).dropna().unique().tolist()
    
    # print(list(filter(lambda x: x.find('RESIDE') > -1 , df.columns.tolist())))
    
    # print for dictionary
    dict_list = df[dictionary].dropna().unique().tolist()
    for x in dict_list:
        #     # if len(x.split('|')) > 2:
        #     #     print(x)
        print(f'\'{x}\':\'VOD_{x}\',')

@elapsedtime
def valid_birthday_tax(df):
    """ valid birthday with TAX.ID """
    
    # very old people
    df['birthday'] = df['DATE.OF.BIRTH'].dropna().astype(int)
    print(df.sort_values(['birthday']).query('birthday < 19200000 & birthday > 0'))
    
    df['VALID_BIRTH'] = (df['NATIONALITY']+'|'+df['TAX.ID']+'|'+df['DATE.OF.BIRTH']).astype(str).map(vld.validate_birthday)
    df['VALID_EMAIL'] = df['EMAIL.1'].map(vld.valid_email)
    
    f_name = f"./output/birth_tax.id_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.xlsx"
    df[['CUSTOMER.CODE','NATIONALITY','DATE.OF.BIRTH','TAX.ID','VALID_BIRTH','RESIDENCE','EMAIL.1','VALID_EMAIL']].to_excel(f_name, index = None, header=True)


def too_many_tylda(val):
    if val == None:
        return '0'
    
    return '1' if len(val.split('~')) > 2 else '0'

@elapsedtime
def accounts(client_type='SME'):

    df = acc.read_accounts_file()

    if client_type == 'SME':
        df = df[df['SECTOR.CU.NATCLI'].isin(['BA', 'CO', 'ET', 'OR'])]
    else: 
        df = df[df['SECTOR.CU.NATCLI'].isin(['RE'])]

    # print('COLUMN LIST',df.columns)   122
    df[['CUSTOMER','ACCOUNT', 'SECTOR.CU.NATCLI', 'CURRENCY']].to_excel(f'acc_{client_type.lower()}.xlsx', index = None, header=True)

    print(df['ACCOUNT'].count(), len(df['ACCOUNT'].unique().tolist()))
    
    
    # get only duplicated list
    #this way is cost effective
    # df_s = pd.concat(g for _, g in df.groupby("CUSTOMER") if len(g) > 1)
    customers = df["CUSTOMER"]
    # df_s = df[customers.isin(customers[customers.duplicated()])].sort_values("CUSTOMER")
    # print('Unique customers num:', len(df_s['CUSTOMER'].unique()))
    # print('Duplicated customers num:', len(df_s))
    df_s = df[customers.duplicated(keep=False)].sort_values("CUSTOMER")
    print('Unique customers num:', len(df['CUSTOMER'].unique().tolist()))
    print('Duplicated customers num:', len(df_s))
    print('Duplicated customers unique num:', len(df_s['CUSTOMER'].unique().tolist()))


    f_name = f'./output/duplicated_acc.id_{date.today().isoformat()}_{client_type}.xlsx'
    print(df_s.groupby(['CUSTOMER']).size().reset_index(name='count'))
    df_s.groupby(['CUSTOMER']).size().reset_index(name='NO.OF.ACCOUNTS').sort_values(['NO.OF.ACCOUNTS'], 
        ascending=False).to_excel(f'./output/{client_type}_CUSTOMER_MORE_ACCOUNTS.xlsx',index = None)
    
    df_s[['CUSTOMER','ACCOUNT', 'SECTOR.CU.NATCLI', 'CURRENCY','REGROUPE','IS.RELATION.OF']].sort_values(['CUSTOMER']).to_excel(f_name, index = None, header=True)

    # df['TYLDA_PROBLEM'] = df['REGROUPE'].astype(str).map(too_many_tylda)

    # df['RATACHE_PROBLEM'] = df.apply(lambda x: '1' if pd.notnull(x['REGROUPE']) and pd.notnull(x['IS.RELATION.TYPE']) else '0', axis=1)

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
    # choose which one
    df_acc = acc.read_accounts_file('RETAIL')
    
    df_acc = df_acc[~df_acc['REGROUPE'].notnull()]
    df_acc = df_acc.drop_duplicates(['CUSTOMER'], keep='first')
    
    df_merged = pd.merge(df_acc, df_cst, left_on='CUSTOMER', right_on='CUSTOMER.CODE')
    # df_merged = df_acc[~df_acc['CUSTOMER'].isin(df_cst['CUSTOMER.CODE'])]
    print('Shape is:', df_merged.shape)

    valid_birthday_tax(df_merged)

    
@elapsedtime
def combain_regroupe():
    df_cst = cst.read_customer_file()
    df_cst['CUSTOMER.CODE'] = df_cst['CUSTOMER.CODE'].astype(str)
    df_acc = acc.read_accounts_file()
    
    #only regrupe are interesting
    df_acc = df_acc[df_acc['REGROUPE'].notnull()]
    
    df_acc = df_acc[df_acc['REGROUPE'].notnull()]
    df_acc['CUSTOMER'] = df_acc['CUSTOMER'].astype(str)

    
    df_reg = df_acc['REGROUPE'].str.split('~',expand=True)
    df_reg = df_reg.rename(columns=lambda x: 'REGROUPE_'+str(x))

    print(df_acc.shape)
    df_acc = pd.concat([df_reg,df_acc], axis=1).reindex(df_reg.index)
    print(df_acc.shape)
    
    # df_acc.to_excel('./output/regroupe.xlsx', index = None, header=True)

    #column to check
    regroupe = 'REGROUPE_2'

    df_merged = pd.merge(df_acc, df_cst, left_on=regroupe, right_on='CUSTOMER.CODE', how='outer', indicator=True)
    df_merged = df_merged[df_merged[regroupe].notnull()]

    print("after notnull",df_merged.shape)

    # left_merged = 'both' #left_only
    left_merged = 'left_only'
    df_regr1 = df_merged.query('_merge == @left_merged')[['ACCOUNT', 'CUSTOMER.CODE','REGROUPE',regroupe]].reset_index(drop=True)
    print(df_regr1.shape, df_regr1)

@elapsedtime
def combine_relations(client_type='SME', save_relations=False, skip_marge=True):
    df_cst = cst.read_customer_file()
    df_cst['CUSTOMER'] = df_cst['CUSTOMER.CODE'].astype(str)
    
    df = acc.read_accounts_file()
    df['CUSTOMER'] = df['CUSTOMER'].astype(str)

    df_acc = df[df['IS.RELATION.OF'].notnull()]
    
    if client_type == 'SME':
        df_acc = df_acc[df_acc['SECTOR.CU.NATCLI'].isin(['BA', 'CO', 'ET', 'OR'])]
    else: 
        df_acc = df_acc[df_acc['SECTOR.CU.NATCLI'].isin(['RE'])]

    # print(f"Number of unique clients: {len(df_acc['CUSTOMER'].unique())}")

    df_rel_to = df_acc['IS.RELATION.OF'].str.split('|',expand=True)
    df_rel_to.rename(columns=lambda x: str(x) +'_RELATION.OF' if x > 9 else '0'+str(x) +'_RELATION.OF', inplace=True)

    # if we want excluded data
    # excluded_clients(df_rel_to, df_cst, df_acc)

    df_rel_type = df_acc['IS.RELATION.TYPE'].str.split('|',expand=True)
    df_rel_type.rename(columns=lambda x: str(x)+'_RELATION.TYPE' if x > 9 else '0'+str(x)+'_RELATION.TYPE', inplace=True)

    df_rat = pd.concat([df_rel_to,df_rel_type], axis=1).reindex(df_rel_to.index)
    
    df_cst = df_cst[['CUSTOMER.CODE', 'NAME.1']]
    cust_dict = df_cst.set_index('CUSTOMER.CODE').to_dict()['NAME.1']

    i =0
    for column in df_rel_to.columns.tolist():
        st = '0'+str(i) if i < 9 else str(i)
        df_rat[f'{st}_CUSTOMER_NAME'] = df_rat[column].map(lambda x: cust_dict.get(x))
        i +=1
    
    # sort columns to get who, and how is in relation
    df_rat = df_rat.reindex(sorted(df_rat.columns), axis=1)

    df_acc = pd.concat([df_rat,df_acc], axis=1).reindex(df_rat.index)   
    columns = ['CUSTOMER','ACCOUNT','ACCOUNT.TITLE.1'] +df_rat.columns.tolist()
    df_acc = df_acc[columns]
    df_acc.to_excel(f'./output/relations_{client_type}.xlsx', index = None, header=True)
    

    if save_relations is True:
        df_acc.to_excel(f'./output/relations_{client_type}.xlsx', index = None, header=True)

    

    
    # i = 0 
    # for column in df_rel_to.columns.tolist():
    #     df_merged = pd.merge(df_cst, df_acc, left_on='CUSTOMER.CODE', right_on=column)
    #     cols = [column, 'NAME.1', df_rel_type.columns.tolist()[i]]
    #     # print(df_merged[cols])
    #     df_merged[cols].to_excel(f'./output/relations_merge_{client_type}_{i}.xlsx', index = None, header=True, sheet_name='RELATIONS')
    #     i +=1
        
        
    # print(df_merged)
    # how_merged = 'both'
    # print(df_merged.query('_merge == @how_merged'))
    # df_merged.query('_merge == @how_merged').to_excel(f'./output/relations_merge_{client_type}.xlsx', index = None, header=True)

    if skip_marge is True:
        return 
    
    # column to check
    rattache = 'IS.RELATION.OF_6'

    df_merged = pd.merge(df_acc, df_cst, left_on=rattache, right_on='CUSTOMER.CODE', how='outer', indicator=True)
    df_merged = df_merged[df_merged[rattache].notnull()]

    # left_merged = 'both' #left_only
    left_merged = 'left_only'
    
    df_rat1 = df_merged.query('_merge == @left_merged')[['ACCOUNT', 'REGROUPE', 'CUSTOMER.CODE','IS.RELATION.OF', rattache]].reset_index(drop=True)
    print(df_rat1.shape, df_rat1.head(70))

@elapsedtime
def excluded_clients(df_rel_to, df_cst, df_acc):
    df_excluded = pd.DataFrame()
    for col in df_rel_to.columns:
        df_m  = df_rel_to[col]
        
        df_m.dropna(inplace=True)
        df_m = df_m.astype(str)
        
        # on customer
        df_m = pd.merge(df_cst, df_m, left_on='CUSTOMER', right_on=col, how='outer', indicator=True)
        columns = ['CUSTOMER','MNEMONIC', col, '_merge']
        df_m = df_m[columns]        
        
        # on account
        # df_m = pd.merge(df_acc, df_m, left_on='CUSTOMER', right_on=col, how='outer', indicator=True)
        # columns = ['ACCOUNT', 'CUSTOMER','IS.RELATION.OF', col, '_merge']
        # df_m = df_m[columns]

        
        # how_merged = 'right_only'
        # df_m = df_m.query('_merge == @how_merged')[columns].reset_index(drop=True).drop(columns=['_merge'])
        # print(df_m.shape)
        df_m = df_m.rename(columns={col: "COLUMN_TO_MERGE"})
        df_excluded = pd.concat([df_excluded,df_m], sort=False)
    
    
    # final clean-up
    df_excluded = df_excluded.drop_duplicates(['COLUMN_TO_MERGE'], keep='first')

    #for account    
    # columns = ['ACCOUNT', 'CUSTOMER','IS.RELATION.OF', 'COLUMN_TO_MERGE', '_merge']
    #for customer
    columns = ['CUSTOMER','SECTOR.CU.NATCLI', 'COLUMN_TO_MERGE', '_merge']
    
    # left_merged = 'both' #left_only #right_only
    # how_merged, column = 'both', 'NOT_ACCOUNT_REL_CUST'
    how_merged, column = 'both', 'ACCOUNT_REL_CUST'

    df_excluded = df_excluded.query('_merge == @how_merged')[columns].reset_index(drop=True).drop(columns=['_merge'])
    df_excluded = df_excluded.rename(columns={'COLUMN_TO_MERGE': column})

    print('FINAL',df_excluded.shape,
        df_excluded[column, 'SECTOR.CU.NATCLI'],
        df_excluded[column].unique())

@elapsedtime
def get_leagal_doc_set():
    types = {
        'CUSTOMER.NO': str,
        'SEQUENCE': str,
        'LEGAL.DOC.NAME': str,
        'LEGAL.HOLDER.NAME': str,
        'LEGAL.ISS.DATE': str,
        'LEGAL.EXP.DATE': str
    }

    common_converters = {
        # 'SMS1':phone_cleaner, # coverts in-place - we want to have the original value
        'EMAIL.1': cnv.to_lowercase
    }

    encoding = 'utf-8'
    f_name = './data/LEGAL.DOC.SET.CSV'

    df = pd.read_csv(f_name, sep=';',
                     encoding=encoding, decimal=',',
                     thousands=' ',
                     dtype=types,
                     # usecols=use_columns,
                     index_col=['CUSTOMER.NO','SEQUENCE'],
                     converters=common_converters,
                     error_bad_lines=False)

    print(df.shape)
    return df

@elapsedtime
def print_leg_dod_dict():
    leg_doc_dict = get_leagal_doc_set().to_dict(orient='index')
    client_docs = [leg_doc_dict[key] for key in leg_doc_dict.keys() if key[0] == 49]
    print(client_docs)



if __name__ == "__main__":
    print(f"File tester - start{datetime.now().strftime('%Y-%m-%dget_leagal_doc_set_%H:%M:%S')}")
    # sector()

    # dictionary_producer('account', 'L.AC.TYPE')
    # dictionary_producer(ProductFiles.LEGAL_DOC, 'LEGAL.DOC.NAME')
    # dictionary_producer(ProductFiles.CUSTOMER, 'MARITAL.STATUS')
    # accounts('RETAIL')
    # combain_regroupe()
    # combine_relations('SME')
    save_xlsx(ProductFiles.CUSTOMER)
    # incorrect_email_address()
    # print_leg_dod_dict()
    # combine_customer_account()
    # read_databe_files()

    print('File tester - end')