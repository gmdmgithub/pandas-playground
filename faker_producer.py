"""
functions for creating fake data - anonimization

All functions based on the same principle if the val is not null return fake val

"""
import util_func as ut
from faker import Faker
import cleaners as cln
import validators_util as vld
import pandas as pd

# french as common lang in Belgium
fake = Faker('fr_FR')
# fake = Faker()
missed_phone_counter = 0
missed_tax_id_counter = 0
missed_email_counter = 0

def first_name(val):
    """Faker with logic related to fake name for female if dict val is FEMALE"""

    if ut.isnull(val):
        return None
    return fake.first_name_female() if val == 'FEMALE' else fake.first_name_male()


def last_name(val):
    return None if ut.isnull(val) else fake.last_name()


def last_name(val):
    return None if ut.isnull(val) else fake.last_name()


def national_register_number(val):
    if ut.isnull(val):
        global missed_tax_id_counter
        missed_tax_id_counter +=1
        return None
    
    return str(fake.random_number(digits=11, fix_len=True))


def document_id(val):
    return None if ut.isnull(val) else fake.random_number()


def street_name(val):
    return None if ut.isnull(val) else fake.street_name()


def street_number(val):
    return None if ut.isnull(val) else fake.building_number()


def apartment(val):
    return None if ut.isnull(val) else fake.building_number()


def city(val):
    return None if ut.isnull(val) else fake.city()


def postalcode(val):
    return None if ut.isnull(val) else fake.postcode()


def email(email, prospect_id):
    # return f'migration.{prospect_id}@vodeno.com' if vld.valid_email(email) == 0 else fake.email()
    
    # if ut.isnull(email):
    if vld.valid_email(email) == 0:
        global missed_email_counter
        missed_email_counter +=1
        return f'migration.{prospect_id}@vodeno.com' 
    return fake.email()


def phone_number(sms, desk_phone):
    """
    Function return fake phone based on SMS.1 and PHONE.1 fields if any is potentially valied returns fake phone number
    Arguments 
        -- sms - is SMS.1 from customer file
        -- desk_phone - is PHONE.1 from customer file
    Return: fake cleaned_phone
    """

    if ((cln.phone_cleaner(sms) is None) and (cln.phone_cleaner(desk_phone) is None)):
        global missed_phone_counter
        missed_phone_counter += 1
        return None 

    return cln.phone_cleaner(fake.phone_number())


def date_of_birth(val):
    return None if ut.isnull(val) else fake.date_of_birth().isoformat()


def future_date(val):
    return None if ut.isnull(val) else fake.future_date().isoformat()


def past_date(val):
    return None if ut.isnull(val) else fake.past_date().isoformat()


def company(val):
    return None if ut.isnull(val) else fake.company()
