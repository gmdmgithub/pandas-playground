import pandas as pd
import numpy as np
import re

import csv

def float_converter(val):
    if not val:
        return None    
    try:
        return np.float(val.replace(' ','').replace(',','.'))
    except:        
        return 'B'

def to_lowercase(val):
    if not val:
        return None    
    try:
        return val.lower()
    except:        
        return val

def phone_cleaner(val):
    if not val:
        return None
    try:
        #remove leading 0, ',' / \ .
        val = re.sub("e[+-]0.*", "", val).lstrip('0').replace(',','').replace('/','').replace('\\','').replace('.','')
        # to be decided
        # if len(val) < 6:
        if len(val) < 3: # many just 1, 2, ? or 65 -  eliminate
            val = None
        return val
    except:        
        return None

def valid_email(val):
    """simple email validation - to consider using python validate_email - existence is possible"""

    if not val:
        return True
    return bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", val))

    #from validate_email import validate_email
    #return validate_email(val,verify=True)

def pandas_way():
    #encoding='ISO-8859-1'
    #encoding='windows-1252'
    col_types ={
        "REGR1":str,
        "REGR2":str,
        "REGR3":str,
        "REGR4":str,
        "REGR5":str
    }
    df_common = pd.read_csv('./data/COMMON.csv', sep=';', 
                            encoding='ISO-8859-1', decimal=',', 
                            thousands=' ',dtype=col_types ) 
    
    # df = pd.read_csv(INPUT_DIR, engine='c', dtype={'FULL': 'str', 'COUNT': 'int'}, header=1)
    # df_common = pd.read_csv('./data/COMMON.csv', sep=';', error_bad_lines=False, index_col=False,  converters={'PAY_STO_EUR':float_converter})
    print(df_common)
    
    df_common_rel = df_common.query('REGR1.notnull() or REGR2.notnull()')
    print(df_common_rel[['CUSTOMER', 'REGR1']].head(10))
    
    #second df frm csv
    col_types = {
        "CODPOS":str
    }
    # set nan if ...
    nan_val = {
       "PHONE":['1']
    }

    common_converters = {
        'GSM':phone_cleaner,
        'PHONE': phone_cleaner,
        'BUREAU': phone_cleaner,
        'EMAIL': to_lowercase
    }

    df_cust = pd.read_csv('./data/CUST.csv', 
                            sep=';', encoding='ISO-8859-1', decimal=',', thousands=' ',
                            dtype=col_types, na_values=nan_val,
                            converters=common_converters) 
        
    
    print(f'Number of records and columns {df_cust.shape}')
    print(f'Number of records in columns: {df_cust.count()}')
    
    # print(dir(df_cust))
    # df_cust['PHONE'] = df_cust['PHONE'].apply(str)
    print(df_cust['PHONE'].head(), df_cust.iloc[:,29].head())

    #check duplicates of phones
    # df_cust_with_phone = df_cust.dropna(subset=['PHONE'])
    # duplicated = df_cust_with_phone[df_cust_with_phone.duplicated(['PHONE'])]
    # print(duplicated[['ID','NAME1','PHONE', 'GSM']])

    # shifted to the function
    # remove e+0
    # df_cust['GSM'] = df_cust['GSM'].map(lambda x: re.sub("e[+-]0.*", "", x)
    #                                      if isinstance(x, str) else np.NaN)
    # df_cust['GSM'] = df_cust['GSM'].map(lambda x: x.lstrip('0').replace(',','').replace('/','').replace('\\','').replace('.','')
    #                                      if isinstance(x, str) else np.NaN)
    
    print(df_cust[['ID','NAME1','PHONE','GSM']].query('GSM.notnull()' or 'PHONE.notnull()').head(50))


    # check the email
    # first take only emails set in the data frame
    df_cust_with_email = df_cust.dropna(subset=['EMAIL'])
    
    # df_cust_with_email.loc[:,'VALID_MAIL'] = df_cust_with_email['EMAIL'].map(valid_email) #.copy()
    df_cust_with_email['VALID_MAIL'] = df_cust_with_email['EMAIL'].map(valid_email) #.copy()

    print(df_cust_with_email[['ID','NAME1','EMAIL', 'VALID_MAIL','GSM']].query('VALID_MAIL == False'))




def csv_way():
    with open('./data/COMMON.csv') as csv_f:
        csv_reader = csv.reader(csv_f,delimiter=';')
        max = 10
        i=0
        for line in csv_reader:
            if i > max:
                break
            print(line[2],line[3], len(line))
            i += 1


if __name__ == "__main__":
    # csv_way()
    pandas_way()

    from validate_email import validate_email
    print(validate_email('jasiek_ala.grybos@gmail.com',verify=True))
