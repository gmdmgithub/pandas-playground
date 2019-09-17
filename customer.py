import pandas as pd
import numpy as np
import re

import phonenumbers as phn

import csv

import cleaners as cln
import validators_util as val
import converters as cnv
from datetime import date
from time import process_time
from faker import Faker

fake = Faker()

def read_customers():

    col_types = {
        "CODPOS":str,
        "PHONE":str,
        "GSM":str
    }
    # set nan if ...
    nan_val = {
       "PHONE":['1']
    }

    common_converters = {
        # 'GSM':phone_cleaner, # coverts in-place - we want to have the original value 
        # 'PHONE': phone_cleaner,
        # 'BUREAU': phone_cleaner,
        'EMAIL': cnv.to_lowercase
    }
    df_customer = pd.read_csv('./data/CUST.csv', 
                            sep=';', encoding='ISO-8859-1', decimal=',', thousands=' ',
                            dtype=col_types, na_values=nan_val,
                            converters=common_converters) 
        
    print(f'Number of records and columns {df_customer.shape}')
    print(f'Number of records in columns: {df_customer.count()}')

    return df_customer

def customer_cleaner():
    df_customer = read_customers()
    
    # print(dir(df_customer))
    # df_customer['PHONE'] = df_customer['PHONE'].apply(str)
    # print(df_customer['PHONE'].head(), df_customer.iloc[:,29].head())

    #check duplicates of phones
    # df_cust_with_phone = df_customer.dropna(subset=['PHONE'])
    # duplicated = df_cust_with_phone[df_cust_with_phone.duplicated(['PHONE'])]
    # print(duplicated[['ID','NAME1','PHONE', 'GSM']])

    # shifted to the function
    # remove e+0
    # df_customer['GSM'] = df_customer['GSM'].map(lambda x: re.sub("e[+-]0.*", "", x)
    #                                      if isinstance(x, str) else np.NaN)
    # df_customer['GSM'] = df_customer['GSM'].map(lambda x: x.lstrip('0').replace(',','').replace('/','').replace('\\','').replace('.','')
    #                                      if isinstance(x, str) else np.NaN)
    
    df_customer['CL_GSM'] = df_customer['GSM'].map(cln.phone_cleaner)
    
    df_customer['CL_PHONE'] = df_customer['PHONE'].map(cln.phone_cleaner)
    df_customer['CL_BUREAU'] = df_customer['BUREAU'].map(cln.phone_cleaner)
    
    
    # let's add country to the GSM
    df_customer['CL_GSM_ADDED_PREFIX'] = (df_customer['DOMICILE'] + df_customer['CL_GSM']).astype(str)
    df_customer['CL_GSM_ADDED_PREFIX'] =  df_customer['CL_GSM_ADDED_PREFIX'].map(cln.phone_prefix_updater)
    # grab more data from spoused to be valid gsm
    df_customer['CL_GSM_VALID'],df_customer['CL_GSM_PREFIX'],df_customer['CL_GSM_SUFFIX'],df_customer['CL_GSM_POSSIBLE'] = zip(*df_customer['CL_GSM_ADDED_PREFIX'].map(val.validate_phone))
    
    # let's do the same for phone number
    df_customer['CL_PHONE_ADDED_PREFIX'] = (df_customer['DOMICILE'] + df_customer['CL_PHONE']).astype(str)
    df_customer['CL_PHONE_ADDED_PREFIX'] =  df_customer['CL_PHONE_ADDED_PREFIX'].map(cln.phone_prefix_updater)
    df_customer['CL_PHONE_VALID'],df_customer['CL_PHONE_PREFIX'],df_customer['CL_PHONE_SUFFIX'],df_customer['CL_PHONE_POSSIBLE'] = zip(*df_customer['CL_PHONE_ADDED_PREFIX'].map(val.validate_phone))

    #and finally with the office phone
    df_customer['CL_BUREAU_ADDED_PREFIX'] = (df_customer['DOMICILE'] + df_customer['CL_BUREAU']).astype(str)
    df_customer['CL_BUREAU_ADDED_PREFIX'] =  df_customer['CL_BUREAU_ADDED_PREFIX'].map(cln.phone_prefix_updater)
    df_customer['CL_BUREAU_VALID'],df_customer['CL_BUREAU_PREFIX'],df_customer['CL_BUREAU_SUFFIX'],df_customer['CL_BUREAU_POSSIBLE'] = zip(*df_customer['CL_BUREAU_ADDED_PREFIX'].map(val.validate_phone))
    df_customer = df_customer.assign(NAME = lambda x: fake.name())
    
    df_customer['VALID_EMAIL'] = df_customer['EMAIL'].map(val.valid_email)

    columns_to_save = [
        'ID','DOMICILE','CTRY','NAME',
        'GSM', 'CL_GSM', 'CL_GSM_ADDED_PREFIX', 'CL_GSM_VALID','CL_GSM_PREFIX','CL_GSM_SUFFIX','CL_GSM_POSSIBLE', 
        'PHONE','CL_PHONE','CL_PHONE_ADDED_PREFIX','CL_PHONE_VALID','CL_PHONE_PREFIX','CL_PHONE_SUFFIX','CL_PHONE_POSSIBLE',
        'BUREAU','CL_BUREAU','CL_BUREAU_ADDED_PREFIX','CL_BUREAU_VALID','CL_BUREAU_PREFIX','CL_BUREAU_SUFFIX','CL_BUREAU_POSSIBLE',
        'EMAIL','VALID_EMAIL']

    df_save = df_customer[columns_to_save]

    print(df_save.head(10))

    # grp = df_save.groupby('CL_GSM') 

    # df_phoned = pd.concat(x for _, x in grp if len(x) >= 2)
    # df_phoned = grp.filter(lambda x: len(x) >= 2)
    
    df_phoned = df_save.groupby(['CL_GSM']).size().reset_index(name='COUNT').query('COUNT > 1')

    
    print(df_phoned.head(20))

    


    # print(df_save.query('GSM.notnull()' or 'PHONE.notnull()').head(50))

    # df_save.to_csv (r'.\\data\\export_dataframe.csv', index = None, header=True)
    df_save.to_excel (r'.\\data\\export_dataframe.xlsx', index = None, header=True)
    
    # f_name = f'.\\data\\duplicate_gsm_customers_{date.today().isoformat()}.xlsx'

    # df_phoned.to_excel (f_name, index = None, header=True)

    

    # # check the email
    # # first take only emails set in the data frame
    # df_cust_with_email = df_customer.dropna(subset=['EMAIL'])
    
    # # df_cust_with_email.loc[:,'VALID_MAIL'] = df_cust_with_email['EMAIL'].map(val.valid_email) #.copy()
    # df_cust_with_email['VALID_MAIL'] = df_cust_with_email['EMAIL'].map(val.valid_email) #.copy()

    # print(df_cust_with_email[['ID','NAME1','EMAIL', 'VALID_MAIL','GSM']].query('VALID_MAIL == False'))

def clean_names():
    start = process_time()

    df = read_customers()
    print('read after', process_time()-start)
    
    df['NAME_HAS_PREFIX'],df['NAME_PREFIX'],df['NAME_CLEANED'] = zip(*df['NAME1'].map(val.subtract_name))

    print('has prefix', process_time()-start)
    
    df['NAME_FIRST'], df['NAME_SURNAME'], df['NAME_EXTRAS'],df['NAME_SUSPECTED_PREFIX']  = zip(*df['NAME_CLEANED'].map(val.split_name))
    
    print('unzip name', process_time()-start)

    df['NAME_FIRST'] = df['NAME1'].map(lambda x: fake.first_name())
    print('first name', process_time()-start)
    df['NAME_SURNAME'] = df['NAME1'].map(lambda x: fake.last_name())
    print('sure name', process_time()-start)
    # df['NAME'] = df['NAME1'].map(lambda x: fake.name())

    # df['NAME'] = [fake.name() for i in range(df.NAME1.size)]
    df['NAME'] = df.index.map(lambda x : fake.name())

    print('fake mapped', process_time()-start)
    
    columns_to_save = [
        'ID','NAME','NAME_SUSPECTED_PREFIX','NAME_HAS_PREFIX','NAME_PREFIX','NAME_CLEANED', 'NAME_FIRST', 'NAME_SURNAME', 'NAME_EXTRAS'
        ]
    print(df[columns_to_save])

    # Counter - suspected prefixes

    # print(df['NAME_SUSPECTED_PREFIX'].value_counts().head(20))

    # from collections import Counter
    # print(dict(Counter(df['NAME_SUSPECTED_PREFIX']).most_common(30)))
    # print(Counter(df['NAME_SUSPECTED_PREFIX']).most_common(30))

    # f_name = '.\\data\\cust_names_'+date.today().isoformat()+'.xlsx'

    # df[columns_to_save].to_excel (f_name, index = None, header=True)


if __name__ == "__main__":
    # customer_cleaner()

    clean_names()

    # from validate_email import validate_email
    # print(validate_email('alex@gmail.com',verify=True))
    # num = phn.parse("+34630992374",None)
    # print(num.country_code, num.national_number)
    # print(num, phn.is_possible_number(num))
    # print(phn.parse("+498469963",None))



def create_rows(num=1):
        output = [{"NAME":fake.name(),
                    'NAME_SURNAME':fake.last_name(),
                    'NAME_FIRST':fake.first_name(),
                   "randomdata":random.randint(1000,2000)} for x in range(num)]
        return output