1. Set type of data-frame field
    a) when reading

``` 
    df = pd.read_csv("sample.csv", sep="\t", dtype={'SAMPLE': str,'VALUE':int64})
```

    b) after creation

```    
        df['SAMPLE'] = df['SAMPLE'].astype(str) 
        or 
        df['SAMPLE'] = df['SAMPLE']..apply(str)
```

2. Similarly, converters can be applied during upload data or after
    a) when reading 

```
        def convert_price_cell(val):
            if not val:
                return None
            return val*2
        
        pd.read_excel("stock_data.xlsx","Sheet2", converters= {
            'PRICE': convert_price_cell
        })
```

    b) on the data-set - drawback speed, advantage can assign to new column 

```
        df['GSM'] = df['GSM'].map(lambda x: re.sub("e[+-]0.*", "", x)
                                       if isinstance(x, str) else np.NaN)
```

3. How to map data from one column and split into more:

```
def some_func(x):
     return x, x**2, x**3, x**4, x**5, x**6 # as many as you need

# - \ sign separate lines
df['p1'], df['p2'], df['p3'], df['p4'], df['p5'], df['p6'] = \ 
     zip(*df['num'].map(some_func))
```

4. Phone validator
https://github.com/daviddrysdale/python-phonenumbers

5. Cool - df.assign - can create multiple columns and operate on as many columns you need

```
df.assign(temp_f=lambda x: x['temp_c'] * 9 / 5 + 32,
           temp_k=lambda x: (x['temp_f'] +  459.67) * 5 / 9)

          temp_c  temp_f  temp_k
Portland    17.0    62.6  290.15
Berkeley    25.0    77.0  298.15
```

6. To select only some types of columns use select_dtypes

```
import numpy as np

drinks = pd.read_csv('http://bit.ly/drinksbycountry')
drinks.select_detypes(include=[np.number])
```

7. iloc and loc difference can be confused - loc - is label iloc is integer location

```
drinks.loc[0:4,:] # print 0 to 4 (including 0 and 4 - means 5 rows)
drinks.ilok[0:4,:]  #prints rows 0 to 3
```

more loc may takes column names
```
# all rows and columns between two labels inclusively 
drinks.loc[:,'country':'wine_servings'] 
```

8. 