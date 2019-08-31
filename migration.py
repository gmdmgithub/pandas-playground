import pandas as pd
import numpy as np
import re

import cleaners as cln
import validators_util as val
import converters as cnv


def perform_test():
    #french lang
    #encoding='ISO-8859-1'
    #encoding='windows-1252'
    
    #encoding='UTF8'

    print("Let's start!")

    ##### FIRST READ COMMON #######
    col_types ={
        "REGR1":str,
        "REGR2":str,
        "REGR3":str,
        "REGR4":str,
        "REGR5":str,
        "CUSTOMER":str
    }
    df_common = pd.read_csv('./data/COMMON.csv', sep=';', 
                            encoding='ISO-8859-1', decimal=',', 
                            thousands=' ',dtype=col_types ) 
    # print(df_common)
    
    ##### THEN READ CUST #######
    col_types = {
        "CODPOS":str,
        "PHONE":str,
        "GSM":str,
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
    
    df_cust = pd.read_csv('./data/CUST.csv', 
                            sep=';', encoding='ISO-8859-1', decimal=',', thousands=' ',
                            dtype=col_types, na_values=nan_val,
                            converters=common_converters) 

    print("CUST data read")

    df_main_union = pd.merge(df_common, df_cust, left_on='CUSTOMER', right_on='ID')
    
    print("first union below")
    print(df_main_union)

    df_regr1_union = pd.merge(df_common, df_cust, left_on='REGR1', right_on='ID')
    df_regr2_union = pd.merge(df_common, df_cust, left_on='REGR2', right_on='ID')
    df_regr3_union = pd.merge(df_common, df_cust, left_on='REGR3', right_on='ID')
    df_regr4_union = pd.merge(df_common, df_cust, left_on='REGR4', right_on='ID')
    df_regr5_union = pd.merge(df_common, df_cust, left_on='REGR5', right_on='ID')
        
    print(df_regr1_union)
    print(df_regr2_union)
    print(df_regr3_union)
    print(df_regr4_union)
    print(df_regr5_union)

    # df_save.to_csv (r'.\data\export_dataframe.csv', index = None, header=True)
    # df_save.to_csv (r'.\data\export_dataframe.csv', index = None, header=True)


if __name__ == "__main__":
    perform_test()


