import functools
from time import process_time 

from datetime import date, datetime
import logging

version = 'v1.0.0'

log_file = f'.\log\migration_logger_{date.today().isoformat()}.log'
formatter = '%(asctime)s;%(name)s;%(message)s'

logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                    format=formatter, filemode='a')

""" ## loging only file
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter(formatter.replace(';',':')))
logging.getLogger().addHandler(stream_handler)
"""

def log_dataset_data(df):
    logging.debug(f'shape of common data is {df.shape}')
    logging.debug(f'more info: \n{df.info}')
    # logging.debug(f'types \n{df.dtypes}')
    logging.debug(f'is nunvaluse in the dataset \n{df.isnull().sum()}')


def elapsedtime(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        # logging
        print(f'function [{func.__name__}] starts at {datetime.now()} ms')
        start_time = process_time()
        try:
            return func(*args, **kwargs)
        finally:    
            #logging
            elapsed_time = process_time() - start_time
            print(f'function [{func.__name__}] finished in {int(elapsed_time * 1000)} ms')
    return new_func

def file_name(product):
    return f"./output/{product}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_transformed_{version}.json"