import requests
import pandas as pd

payload ={
    "name": "Alex",
    "job": "programmer"
}

headers = {
    "Authorization": "Bearer sdfjkdsjfs088gftdd",
    "accesskey": "accesskey",  # provided accesskey
}

r = requests.post('https://reqres.in/api/users', json=payload)
# r = requests.post('https://reqres.in/api/users', json=payload, headers=headers)

# print(help(r))
print(r.text)

print(pd.__version__)
print(pd.show_versions())