"""
functions for creating fake data - anonimization

All functions based on the same principle if the val is not null return fake val

"""

from faker import Faker

# french as common lang in Belgium
fake = Faker('fr_FR')
# fake = Faker()

def first_name(val):
    """the only logic related to fake name for female if dict val is FEMALE"""
    
    if not val:
        return None
    return fake.first_name_female() if val == 'FEMALE' else fake.first_name_male()

def last_name(val):
    return None if not val else fake.last_name()

def last_name(val):
    return None if not val else fake.last_name()

def national_register_number(val):
    return None if not val else fake.random_number(digits=11, fix_len=True)

def document_id(val):
    return None if not val else fake.random_number()

def street_name(val):
    return None if not val else fake.street_name()

def street_number(val):
    return None if not val else fake.building_number()

def apartment(val):
    return None if not val else fake.building_number()

def city(val):
    return None if not val else fake.city()

def postalcode(val):
    return None if not val else fake.postcode()

def email(val):
    return None if not val else fake.email()

def phone_number(val):
    return None if not val else fake.phone_number()

def date_of_birth(val):
    return None if not val else fake.date_of_birth().isoformat()

def future_date(val):
    return None if not val else fake.future_date().isoformat()

def past_date(val):
    return None if not val else fake.past_date().isoformat()

def company(val):
    return None if not val else fake.company()
