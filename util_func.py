import pandas as pd
import numpy as np
import re
import functools
from time import process_time 

from datetime import date
import logging

log_file = f'migration_logger_{date.today().isoformat()}.log'
formatter = '%(asctime)s;%(name)s;%(message)s'

logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                    format=formatter, filemode='a')


stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter(formatter.replace(';',':')))
logging.getLogger().addHandler(stream_handler)

def elapsedtime(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        start_time = process_time()
        func(*args, **kwargs)
        elapsed_time = process_time() - start_time
        print('function [{}] finished in {} ms'.format(
            func.__name__, int(elapsed_time * 1000)))
    return newfunc

@elapsedtime
def read_concat_data():
    # read some data from several files and merge into one
    file_list = ['sample1.csv', 'sample2.csv','sample3.csv']

    df = pd.concat((pd.read_csv(f) for f in file_list),ignore_index=True) #ignore_index to refresh index
    print(df.head())

    # read from directory and pattern files - this time columns not rows will be concat
    from glob import glob
    my_files = sorted(glob('sample_columns*.csv'))
    df = pd.concat((pd.read_csv(f) for f in my_files),ignore_index=True, axis='columns') #ignore_index to refresh index

def generate_df():
    
    df = pd.DataFrame(np.random.rand(5,6))# rows,columns
    print(df)
    # rename columns to get more readable
    df = df.rename({0:'first'}, axis='columns')
    # df.columns = df.columns.str.replace('1','second') #- problem column is not a string 
    df = df.add_prefix('A_')
    df = df.add_suffix('_E')
    print(df)
    
    df = pd.DataFrame({'Names':['Alex', 'Marcia'],'Score':[25,40]})
    # concat - argument must be an iterable of pandas objects
    df = pd.concat([df, pd.DataFrame({'Names':['John'],'Score':[12]})])
    print(df)

@elapsedtime
def reverse_rows_columns():
    df = pd.DataFrame({'Names':['Adam', 'Alex', 'John', 'Marry'], 'Score':['3','1','-','7']})
    print('Origin')
    print(df)

    # first column
    print('Rows')
    df = df.loc[::-1]
    print(df)
    df = df.reset_index(drop=True)
    print(df)
    #now columns
    print('Columns')
    df = df.loc[:,::-1] #first rows, second columns
    print(df)

    # convert to numeric
    # df['Score'] = pd.to_numeric(df.Score, errors='coerce') 
    # fill Nan with some value - here 0
    df['Score'] = pd.to_numeric(df.Score, errors='coerce').fillna(0)
    print(df)

    # filter only Adam and Alex
    # df = df.loc[(df['Names'] =='Alex') | (df['Names'] =='Adam')]
    df = df.loc[df['Names'].str.contains('alex|adam', flags=re.I, regex=True)]
    print(df)
    # df.reset_index(inplace=True) # old still exists 
    # print(df)
    df.reset_index(drop=True, inplace=True)
    print(df)

def clipboard_reader():
    # remember to have something into the clipboard
    print(pd.read_clipboard())


def log_dataset_data(df):
    logging.debug(f'shape of common data is {df.shape}')
    # logging.debug(f'more info: \n{df.info}')
    logging.debug(f'types \n{df.dtypes}')
    logging.debug(f'is nunvaluse in the dataset \n{df.isnull().sum()}')


if __name__ == '__main__':
    # read_concat_data()
    # generate_df()
    reverse_rows_columns()
    # clipboard_reader()