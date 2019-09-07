import pandas as pd

import json

from pandas.io.json import json_normalize
# json_normalize

# df = pd.read_json('.\\app_script.json')
# df.to_csv(r'.\\app_script.csv', index = None, header=True)

with open('.\\app_script.json') as f:
    data = json.load(f)

df = json_normalize(data)
print (df)
df.to_csv(r'.\\app_script.csv', index = None, header=True)