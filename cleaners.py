import re
import phonenumbers as phn
import validators_util as vld
import pandas as pd
import util_func as ut

MINIMAL_PHONE_LENGTH = 5


def phone_cleaner(val):
    """
    clears phone number - often written with free hand, only digits are interesting

    Arguments -- val: single cell
    Return: phone number as a number
    """

    if ut.isnull(val):
        return None
    try:
        # sometimes numbers are in exponential notation
        val = re.sub("e[+-]0.*", "", val).lstrip('0')
        # only digits
        val = re.sub("\D", "", val)
        # TODO?? Ask busines minimal length
        if len(val) <= MINIMAL_PHONE_LENGTH:  # many just 1, 2, ? or 65 -  eliminate
            val = None
        return val
    except:
        return None


def get_country_phone_code(country_iso):
    """
    Function returns country code phone based on ISO country name

    Arguments -- ISO country code ie Belgium: BL
    Return: phone prefix fro a country ie Belgium 32
    """
    if not country_iso:
        return None
    country_iso = str(country_iso)
    for code, iso in phn.COUNTRY_CODE_TO_REGION_CODE.items():
        if country_iso.upper() in iso:
            return str(code)

    return None


def phone_prefix_updater(val):
    """"
    Function updates country prefix for the phone

    Arguments -- aggregated cell value - ISO country + cleaned phone number 
    Return: phone number with country code
    """
    if ut.isnull(val):
        return None
    # looking only for country prefix
    iso = re.sub('[^A-Za-z]', "", val)
    cleared_phone = re.sub(r"\D", "", val)

    country_phone_prefix = get_country_phone_code(iso)

    if country_phone_prefix is None:
        return cleared_phone

    # it means for sure country code is in the scope of phone number
    if len(cleared_phone) > 8 and cleared_phone.startswith(country_phone_prefix):
        return cleared_phone

    return f'{country_phone_prefix}{cleared_phone}'


def normalize_email(val):
    """
    clears phone number - often written with free hand, only digits are interesting

    Arguments -- val: single cell
    Return: phone number as a number
    """
    if ut.isnull(val):
        return None

    val = val.lower()
    # check if valid - if not return the same
    if not vld.valid_email(val):
        return val

    # remove . before @
    val = val.split('@')
    username = val[0].replace('.', '')
    return f'{username}@{val[1]}'


def document_type(val):
    """
    cleans document_type field - temporary solution

    Arguments -- val: single cell
    Return: first in a pipeline document type
    """
    # TODO!!! -document type should be returned in different way
    if ut.isnull(val):
        return None
    val = str(val)
    # for the security
    val = val.strip('|').split('|')
    return val[0] if len(val) > 0 else None
