import functools
from time import process_time 
import pandas as pd

from datetime import date, datetime
import logging

version = 'v1.0.0'

log_file = f'.\log\migration_logger_{date.today().isoformat()}.log'
formatter = '%(asctime)s;%(name)s;%(message)s'

logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format=formatter, filemode='a')

# """ ## if loging only to file uncomment
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter(formatter.replace(';',':')))
logging.getLogger().addHandler(stream_handler)
# """

def log_dataset_data(df):
    """
    Simple func to log data about pandas DataFrame
    
    Arguments -- DataFrame
    """
    logging.info(f'shape of common data is {df.shape}')
    logging.debug(f'more info: \n{df.info}')
    logging.debug(f'types \n{df.dtypes}')
    logging.debug(f'is nunvaluse in the dataset \n{df.isnull().sum()}')


def elapsedtime(func):
    """
    Function wrapper (decorator) to estimate execution time
    
    Arguments -- func to wrap
    Return: what func return
    """
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        logging.info(f'function [{func.__name__}] starts at {datetime.now()} ms')
        logging.info(f'Running "{func.__name__}" with arguments {args}')
        start_time = process_time()
        try:
            return func(*args, **kwargs)
        finally:    
            #logging
            elapsed_time = process_time() - start_time
            logging.info(f'function [{func.__name__}] finished in {int(elapsed_time * 1000)} ms')
    return new_func

def file_name(product, ext='json'):
    """
    Create a filename string expected in the project 
    
    Arguments -- 
    - product - product name
    - ext - file extension default 'json'
    Return: file name with timestamp
    """
    return f"./output/{product}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_transformed_{version}.{ext}"

def isnull(pd_val):
    """Function solve the problem that empty string is not a NaN val for pandas"""
    
    return (pd.isnull(pd_val) or len(pd_val.strip()) == 0) if isinstance(pd_val, str) else pd.isnull(pd_val)

def agreements_producer(client='RETAIL'):
    ag = {
            "date": "2019-12-01",
            "agree": True,
            "code": "RETAIL_STANDARD_TNC_ACCEPTANCE",
            "version": "1.0"
        }
    ag1, ag2, ag3, ag4,ag5,ag6 = ag.copy() , ag.copy(), ag.copy(), ag.copy(), ag.copy(), ag.copy()

    if client == 'RETAIL':
        # ag1 is ok
        ag2["code"] = "RETAIL_PREMIUM_TNC_ACCEPTANCE"
        ag3["code"] = "RETAIL_STANDARD_FEES_AND_CHARGES"
        ag4["code"] = "RETAIL_PREMIUM_FEES_AND_CHARGES"
        ag5["code"] = "RETAIL_STANDARD_DPGS"
        ag6["code"] = "RETAIL_PREMIUM_DPGS"
        
        return ag1,ag2,ag3,ag4,ag5,ag5
    
    ag1["code"] = "SME_STANDARD_TNC_ACCEPTANCE"
    ag2["code"] = "SME_PREMIUM_TNC_ACCEPTANCE"
    ag3["code"] = "SME_STANDARD_FEES_AND_CHARGES"
    ag4["code"] = "SME_PREMIUM_FEES_AND_CHARGES"
    ag5["code"] = "SME_STANDARD_DPGS"
    ag6["code"] = "SME_PREMIUM_DPGS"
    return ag1,ag2,ag3,ag4,ag5,ag5

def consents_producer():
    cp1 = {
            "date": "2019-12-01",
            "agree": False,
            "code": "PRIVACY_POLICY",
            "version": "1.0"
        }
    cp2, cp3,cp4 = cp1.copy(), cp1.copy(), cp1.copy()
    cp2 ["code"] = "GENERAL_MARKETING_CONSENT"
    cp3 ["code"] = "THIRD_PARTIES_MARKETING_CONSENT"
    cp4 ["code"] = "ELECTRONIC_MARKETING_CONSENT"
    
    return cp1,cp2,cp3,cp4
    
