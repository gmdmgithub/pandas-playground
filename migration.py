import pandas as pd
import numpy as np

import csv

def float_converter(val):
    if not val:
        return None    
    try:
        return np.float(val.replace(' ','').replace(',','.'))
    except:        
        return 'B'

def pandas_way():
    #encoding='ISO-8859-1'
    #encoding='windows-1252'
    #temp = u"""ALV 0 %
    # 1 177,44
    # 1 032,06
    # 1 239,09
    # 784,86
    # 936,27"""
    # pd.read_csv(pd.compat.StringIO(temp), sep=';', decimal=',', thousands=' ')

    df_common = pd.read_csv('./data/COMMON.csv', sep=';', encoding='ISO-8859-1', decimal=',', thousands=' ') 
    # df = pd.read_csv(INPUT_DIR, engine='c', dtype={'FULL': 'str', 'COUNT': 'int'}, header=1)
    # df_common = pd.read_csv('./data/COMMON.csv', sep=';', error_bad_lines=False, index_col=False,  converters={'PAY_STO_EUR':float_converter})
    print(df_common.head())

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
