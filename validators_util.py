import re
import pandas as pd
import validators
import util_func as ut


def valid_email(val):
    """
    simple email validation - to consider using python validate_email - existence is possible
    
    Arguments -- val: single cell
    Return: 0 - not valied, 1 valied
    """

    if ut.isnull(val):
        return 0
    
    #from validate_email import validate_email
    # return validate_email(val,verify=True)

    #for more than one we pick-up first
    if len(val.split('|')) > 0 and len(val.split('|')[0]) > 0:
        val = val.split('|')[0]

    return 0 if not validators.email(val) else 1


def validate_birthday(val):
    """
    For a belgium validate birthday and Registry number

    In T24 R11 TAX.ID is unique and mandatory if the RESIDENCE is BE.  A check is be made on the national register number in Belgium which is composed of 11 digits:

    the first 6 positions form the date of birth in the opposite direction. For a person born on July 30, 1985, his first 6 numbers are 850730;
    The following 3 positions constitute the daily birth counter. This figure is even for women and odd for men; • the last 2 positions constitute the check digit. This check digit is a sequence of 2 digits.
    This number is the complement of 97 of the modulo 97 of the number formed:

    - by the first 9 digits of the national number for persons born before 1 January 2000;

    - by the number 2 followed by the first 9 digits of the national number for persons born after 31 December 1999.

    Checks only Belgium customers
     Arguments -- val: three piped cells  - Country code | tax.id | birth_day
    Return: 
    - True/False -
    """
    if ut.isnull(val):
        return False
    
    val = str(val)
    val = val.split('|')
    if len(val) != 3:
        return False
    
    if val[0] != 'BE':
        return True
    if len(val) <3 :
        return False
    
    tax_id = val[1]
    tax_id = re.sub(r"\D", "", tax_id)
    if len(tax_id) != 11:
        return False
    if val[2][0] == '2':
        tax_id = '2'+tax_id
    
    check_num, val_num = int(tax_id[-2:]), int(tax_id[:-2])
    belgium_modulo_number = 97
    
    return (belgium_modulo_number - val_num % belgium_modulo_number) == check_num
