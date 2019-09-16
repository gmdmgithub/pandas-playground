import pandas as pd
import numpy as np
import re

import cleaners as cln
import validators_util as val
import converters as cnv
import util_func as ut
from datetime import date, time, datetime

import logging  

col_types ={
    "REGR1":str,
    "REGR2":str,
    "REGR3":str,
    "REGR4":str,
    "REGR5":str,
    "CUSTOMER":str
}


def perform_test():
    start = time.process_time()
    #french lang
    #encoding='ISO-8859-1'
    #encoding='windows-1252'
    
    #encoding='UTF8'
    ##### FIRST READ COMMON #######
    print("Let's start!")

   
    df_common = pd.read_csv('./data/COMMON.csv', sep=';', 
                            encoding='ISO-8859-1', decimal=',', 
                            thousands=' ',dtype=col_types ) 
    # print(df_common)
    
    ##### THEN READ CUST #######
    col_types = {
        "CODPOS":str,
        "PHONE":str,
        "GSM":str,
        "CUS1":str,
        "ID":str
    }
    # set nan if ...
    nan_val = {
       "PHONE":['1']
    }

    common_converters = {
        # 'GSM':phone_cleaner,
        # 'PHONE': phone_cleaner,
        # 'BUREAU': phone_cleaner,
        'EMAIL': cnv.to_lowercase
    }
    


    print("COMMON data read")
    
    df_customer = pd.read_csv('./data/CUST.csv', 
                            sep=';', encoding='ISO-8859-1', decimal=',', thousands=' ',
                            dtype=col_types, na_values=nan_val,
                            converters=common_converters) 

    ut.log_dataset_data(df_customer)

    logging.debug('Customer read')
    
    df_customer_cs1 = df_customer.copy()
    df_customer_cs1['CS1_ID'] = df_customer_cs1['CUS1']

    df_customer_cs1 = df_customer_cs1[['CS1_ID']]

    print(df_customer_cs1.query('CS1_ID.notnull()').head(20))



    df_customer['CL_GSM'] = df_customer['GSM'].map(cln.phone_cleaner)
    
    df_customer['CL_PHONE'] = df_customer['PHONE'].map(cln.phone_cleaner)
    
    
    # let's add country to the GSM
    df_customer['CL_GSM_ADDED_PREFIX'] = (df_customer['DOMICILE'] + df_customer['CL_GSM']).astype(str)
    df_customer['CL_GSM_ADDED_PREFIX'] =  df_customer['CL_GSM_ADDED_PREFIX'].map(cln.phone_prefix_updater)
    # df_customer['CL_GSM_CC'] = df_customer['DOMICILE'].map(cln.get_country_phone_code)
    # grab more data from spoused to be valid gsm
    df_customer['CL_GSM_VALID'],df_customer['CL_GSM_PREFIX'],df_customer['CL_GSM_SUFFIX'],df_customer['CL_GSM_POSSIBLE'] = zip(*df_customer['CL_GSM_ADDED_PREFIX'].map(val.validate_phone))
    
    # let's do the same for phone number
    df_customer['CL_PHONE_ADDED_PREFIX'] = (df_customer['DOMICILE'] + df_customer['CL_PHONE']).astype(str)
    df_customer['CL_PHONE_ADDED_PREFIX'] =  df_customer['CL_PHONE_ADDED_PREFIX'].map(cln.phone_prefix_updater)
    
    df_customer['CL_PHONE_VALID'],df_customer['CL_PHONE_PREFIX'],df_customer['CL_PHONE_SUFFIX'],df_customer['CL_PHONE_POSSIBLE'] = zip(*df_customer['CL_PHONE_ADDED_PREFIX'].map(val.validate_phone))

    df_customer['VALID_EMAIL'] = df_customer['EMAIL'].map(val.valid_email)


    df_main_union = pd.merge(df_common, df_customer, left_on='CUSTOMER', right_on='ID')
    
    print("first union below")
    print(df_main_union)

    df_regr1_union = pd.merge(df_common, df_customer, left_on='REGR1', right_on='ID')
    df_regr2_union = pd.merge(df_common, df_customer, left_on='REGR2', right_on='ID')
    df_regr3_union = pd.merge(df_common, df_customer, left_on='REGR3', right_on='ID')
    df_regr4_union = pd.merge(df_common, df_customer, left_on='REGR4', right_on='ID')
    df_regr5_union = pd.merge(df_common, df_customer, left_on='REGR5', right_on='ID')

    df_cus1_union = pd.merge(df_main_union, df_customer_cs1, left_on='ID', right_on='CS1_ID')
    df_cus1_union = pd.merge(df_common, df_cus1_union, left_on='CUSTOMER', right_on='ID')

    
        
    print(df_regr1_union)
    print(df_regr2_union)
    print(df_regr3_union)
    print(df_regr4_union)
    print(df_regr5_union)

    print(df_cus1_union)


    columns_to_save = ['ID',
        'GSM', 'CL_GSM', 'CL_GSM_ADDED_PREFIX', 'CL_GSM_VALID','CL_GSM_PREFIX','CL_GSM_SUFFIX','CL_GSM_POSSIBLE', 
        'PHONE','CL_PHONE','CL_PHONE_ADDED_PREFIX','CL_PHONE_VALID','CL_PHONE_PREFIX','CL_PHONE_SUFFIX','CL_PHONE_POSSIBLE',
        'EMAIL','VALID_EMAIL']

    df_main_union = df_main_union[columns_to_save]
    df_regr1_union = df_regr1_union[columns_to_save]
    df_regr2_union= df_regr2_union[columns_to_save]
    df_regr3_union= df_regr3_union[columns_to_save]
    df_regr4_union= df_regr4_union[columns_to_save]
    df_regr5_union= df_regr5_union[columns_to_save]


    df_regr1_union = pd.merge(df_common, df_regr1_union, left_on='CUSTOMER', right_on='ID')
    df_regr2_union = pd.merge(df_common, df_regr2_union, left_on='CUSTOMER', right_on='ID')
    df_regr3_union = pd.merge(df_common, df_regr3_union, left_on='CUSTOMER', right_on='ID')
    df_regr4_union = pd.merge(df_common, df_regr4_union, left_on='CUSTOMER', right_on='ID')
    df_regr5_union = pd.merge(df_common, df_regr5_union, left_on='CUSTOMER', right_on='ID')

    df_regr1_union = df_regr1_union[columns_to_save]
    df_regr2_union= df_regr2_union[columns_to_save]
    df_regr3_union= df_regr3_union[columns_to_save]
    df_regr4_union= df_regr4_union[columns_to_save]
    df_regr5_union= df_regr5_union[columns_to_save]
    
    
    df_cus1_union= df_cus1_union[columns_to_save]
    df_cus1_union = df_cus1_union.drop_duplicates()

    # df_save.to_csv (r'.\data\export_dataframe.csv', index = None, header=True)
    # df_save.to_csv (r'.\data\export_dataframe.csv', index = None, header=True)

    f_name = f'.\\data\\output_{date.today().isoformat()}.xlsx'
    before_save = (time.process_time() - start)
    print(f'Elapsed time before save file is {before_save}')

    with pd.ExcelWriter(f_name) as writer:  # doctest: +SKIP
        df_main_union.to_excel(writer, sheet_name='MAIN_ACTIVE_USERS', index = None, header=True)
        df_regr1_union.to_excel(writer, sheet_name='REGR1_USERS', index = None, header=True)
        df_regr2_union.to_excel(writer, sheet_name='REGR2_USERS', index = None, header=True)
        df_regr3_union.to_excel(writer, sheet_name='REGR3_USERS', index = None, header=True)
        df_regr4_union.to_excel(writer, sheet_name='REGR4_USERS', index = None, header=True)
        df_regr5_union.to_excel(writer, sheet_name='REGR5_USERS', index = None, header=True)
        df_cus1_union.to_excel(writer, sheet_name='CUS1_USERS', index = None, header=True)

    # df_main_union.to_excel (r'.\\data\\active_main.xlsx', index = None, header=True)
    # df_regr1_union.to_excel (r'.\\data\\regr1_main.xlsx', index = None, header=True)
    # df_regr2_union.to_excel (r'.\\data\\regr2_main.xlsx', index = None, header=True)
    # df_regr3_union.to_excel (r'.\\data\\regr3_main.xlsx', index = None, header=True)
    # df_regr4_union.to_excel (r'.\\data\\regr4_main.xlsx', index = None, header=True)
    # df_regr5_union.to_excel (r'.\\data\\regr5_main.xlsx', index = None, header=True)

    # df_cus1_union.to_excel (r'.\\data\\cus1_main.xlsx', index = None, header=True)

    elapsed_time = (time.process_time() - start)
    print(f'Total elapsed time is: {elapsed_time}')

def new_files():
    df = pd.read_csv('./data/COMMON-06-09.csv',sep=';',
                            encoding='ISO-8859-1', decimal=',', 
                            thousands=' ',dtype=col_types )
    
    print(df['NATURE'].unique().tolist())
    print(df['CIVIL'].unique().tolist())
    print(df['SEC_LIB'].unique().tolist())
    print(df['SECTOR'].unique().tolist())
    print(df['SECTOR'].unique().tolist())


    df_c = pd.read_csv('./data/CUSTOMER-06-09.csv',sep=';',
                            encoding='ISO-8859-1', decimal=',', 
                            thousands=' ',dtype=col_types )
    
    print(df_c['TYPE'].unique().tolist())
    print(df_c['TITLE'].unique().tolist())

    print(df_c.info())

    sector = df['SECTOR'].value_counts()

    print(sector.loc[sector.index < 2000])

    # print(df[df.groupby('SECTOR')['SECTOR'].transform('size') > 1])
    # Table_name.groupby(['Group'])['Feature'].aggregation()
    non_null_count = df.groupby(['SECTOR'])['REGR4'].count() # for field REGR4 count grouped by sector 
    print(non_null_count)

    df.groupby(['SECTOR'])


    # df['NAME1'] = 
    # print(df['NAME1'].str.split(" ", expand=True))

def sector():
    import chardet
    with open('./data/SECTOR.1909081335.MULTIVALUE.CSV','rb') as f:
        # print(f)
        result = chardet.detect(f.read())  # or readline if the file is large
        print('Chart detector',result['encoding'])


    # encoding = 'latin1'
    # encoding = 'ISO-8859-1'
    # encoding = 'cp1250'
    # encoding = 'UTF-8'
    # encoding = 'UTF-8'
    # encoding = 'ISO-8859-9'
    encoding = 'windows-1255'

    read_columns = ['Id','Fieldname','Value']
    
    df = pd.read_csv('./data/SECTOR.1909081335.MULTIVALUE.CSV',sep=';',
                            encoding=encoding, decimal=',', usecols=read_columns, # reads only selected columns
                            thousands=' ', dtype=col_types)
    
    # logging.debug(df.info(memory_usage='deep'))
    print(df.tail(10))

    ut.log_dataset_data(df)

def test_df():
    encoding = 'latin1'
    f_name = './data/COUNTRY.1909081337.MULTIVALUE.CSV'
    df = pd.read_csv(f_name,sep=';',
                            encoding=encoding, decimal=',', #usecols=read_columns, # reads only selected columns
                            thousands=' ', dtype=col_types)
    
    # logging.debug(df.info(memory_usage='deep'))
    print(df.head(40))

    ut.log_dataset_data(df)
    

if __name__ == "__main__":
    # perform_test()
    # new_files()
    # sector()
    test_df()


