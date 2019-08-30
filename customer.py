import pandas as pd
import numpy as np
import re

import phonenumbers as phn

import csv

import cleaners as cln
import validators as val
import converters as cnv


def customer_cleaner():
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
    
    
    df_customer['CL_GSM_ADDED_PREFIX'] = (df_customer['DOMICILE'] + df_customer['CL_GSM']).astype(str)
    # df_customer['CL_GSM_CC'] = df_customer['CL_GSM_CC'].astype(str)
    df_customer['CL_GSM_ADDED_PREFIX'] =  df_customer['CL_GSM_ADDED_PREFIX'].map(cln.phone_prefix_updater)

    df_customer['CL_GSM_CC'] = df_customer['DOMICILE'].map(cln.get_country_phone_code)


    df_customer['CL_GSM_VALID'],df_customer['CL_GSM_PREFIX'],df_customer['CL_GSM_SUFFIX'],df_customer['CL_GSM_POSSIBLE'] = zip(*df_customer['CL_GSM_ADDED_PREFIX'].map(val.validate_phone))
    df_customer['CL_PHONE_VALID'],df_customer['CL_PHONE_PREFIX'],df_customer['CL_PHONE_SUFFIX'],df_customer['CL_PHONE_POSSIBLE'] = zip(*df_customer['CL_PHONE'].map(val.validate_phone))

    df_customer['VALID_EMAIL'] = df_customer['EMAIL'].map(val.valid_email)

    df_save = df_customer[['ID',
                        'GSM', 'CL_GSM', 'CL_GSM_ADDED_PREFIX', 'CL_GSM_VALID','CL_GSM_PREFIX','CL_GSM_SUFFIX','CL_GSM_POSSIBLE', 
                        'PHONE','CL_PHONE','CL_PHONE_VALID','CL_PHONE_PREFIX','CL_PHONE_SUFFIX','CL_PHONE_POSSIBLE',
                        'EMAIL','VALID_EMAIL']]
    print(df_save.query('GSM.notnull()' or 'PHONE.notnull()').head(50))


    # df_save.to_csv (r'.\\data\\export_dataframe.csv', index = None, header=True)
    df_save.to_excel (r'.\\data\\export_dataframe.xlsx', index = None, header=True)

    

    # # check the email
    # # first take only emails set in the data frame
    # df_cust_with_email = df_customer.dropna(subset=['EMAIL'])
    
    # # df_cust_with_email.loc[:,'VALID_MAIL'] = df_cust_with_email['EMAIL'].map(val.valid_email) #.copy()
    # df_cust_with_email['VALID_MAIL'] = df_cust_with_email['EMAIL'].map(val.valid_email) #.copy()

    # print(df_cust_with_email[['ID','NAME1','EMAIL', 'VALID_MAIL','GSM']].query('VALID_MAIL == False'))



if __name__ == "__main__":
    customer_cleaner()

    # from validate_email import validate_email
    # print(validate_email('alex@gmail.com',verify=True))
    # num = phn.parse("+34630992374",None)
    # print(num.country_code, num.national_number)
    # print(num, phn.is_possible_number(num))
    # print(phn.parse("+498469963",None))

