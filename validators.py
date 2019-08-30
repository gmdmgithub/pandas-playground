import re

def valid_email(val):
    """simple email validation - to consider using python validate_email - existence is possible"""

    if not val:
        return False
    return bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", val))


def validate_phone(val):
    if not val:
        return False, None, None, False
    try:
        num = phn.parse('+'+val,None)
        return True, num.country_code, num.national_number, phn.is_possible_number(num)
    except:
        return False, None, None, False