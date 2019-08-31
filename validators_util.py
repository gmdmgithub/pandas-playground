import re
import phonenumbers as phn
# from phonenumbers import COUNTRY_CODE_TO_REGION_CODE

import validators

def valid_email(val):
    """simple email validation - to consider using python validate_email - existence is possible"""

    if not val:
        return False
    # more complex email validator
    # return bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", val))
    if not validators.email(val):
        return False
    return True

    #from validate_email import validate_email
    #return validate_email(val,verify=True)


def validate_phone(val):
    if not val:
        return False, None, None, False
    try:
        num = phn.parse('+'+val,None)
        return True, str(num.country_code), str(num.national_number), phn.is_possible_number(num)
    except:
        return False, None, None, False

