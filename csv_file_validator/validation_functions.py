"""
validation_functions module
"""
import os
import re
import logging
import functools
from datetime import datetime
from dateutil import parser

LOGGER = logging.getLogger(__name__)


def _get_logged_error(func_name, **kwargs):
    """
    function responsible for handling the logging of the failed validations
    :param func_name:
    :param type:
    :param kwargs:
    :return:
    """
    logged_string = f'{func_name} - failed to meet this value : {kwargs.get("validation_value")}'

    if kwargs.get("row_number"):
        logged_string += f' - Row#: {kwargs["row_number"]}'
    if kwargs.get("column"):
        logged_string += f' - Column name: {kwargs["column"]}'
    if kwargs.get("column_value"):
        logged_string += f' - Column value: {kwargs["column_value"]}'
    if kwargs.get("Exception"):
        logged_string += f' - Exception: {kwargs["Exception"]}'

    LOGGER.error(logged_string)


def logging_decorator(func):
    """
    logging decorator for validation functions
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper_decorator(**kwargs):
        try:
            validation_result = func(**kwargs)
        except (ValueError, TypeError, KeyError, IndexError, AttributeError, ArithmeticError) \
                as err:
            # in case validation function raised Error,
            # we still need to add one more failed validation
            # for the __main__ error counter
            validation_result = 1
            kwargs["Exception"] = err
        except Exception as exc:
            raise RuntimeError(f'Unexpected Exception {exc} in {func.__name__}')

        if validation_result != 0:
            _get_logged_error(func_name=func.__name__, **kwargs)

        return validation_result

    return wrapper_decorator


@logging_decorator
def check_file_extension(**kwargs):
    """
    validation function checking the file extension is equal to the expected value
    :param kwargs:
    :return:
    """
    if os.path.splitext(kwargs.get("file_name"))[1][1:] == kwargs.get("validation_value"):
        return 0
    return 1


@logging_decorator
def check_file_mask(**kwargs):
    """
    validation function checking the file name file mask against a provided regex expr.
    :param kwargs:
    :return:
    """
    file = os.path.split(kwargs.get("file_name"))[-1]
    dot_index = file.rfind(".")
    filename = file[:dot_index]
    result = re.match(kwargs.get("validation_value"), filename)

    if result:
        return 0
    return 1


@logging_decorator
def check_file_size_range(**kwargs):
    """
    validation function checking file size in MB is inside a numeric range
    provided by the list of int values [min value, max value]
    :param kwargs:
    :return:
    """
    if kwargs.get("validation_value")[1] >= \
            kwargs.get("file_size") >= \
            kwargs.get("validation_value")[0]:
        return 0
    return 1


@logging_decorator
def check_file_row_count_range(**kwargs):
    """
    validation function checking file row count is inside a numeric range
    provided by the list of int values [min value, max value]
    :param kwargs:
    :return:
    """
    if kwargs.get("validation_value")[0] <= \
            kwargs.get("file_row_count") <= \
            kwargs.get("validation_value")[1]:
        return 0
    return 1


@logging_decorator
def check_file_header_column_names(**kwargs):
    """
    validation function checking file header row is equal to the expected header row
    :param kwargs:
    :return:
    """
    if kwargs.get("validation_value") == kwargs.get("file_header"):
        return 0
    return 1


@logging_decorator
def check_column_allow_data_type(**kwargs):
    """
    validation function checking column value data type is equal to the expected data type
    :param kwargs:
    :return:
    """
    if kwargs.get("validation_value") == "str":
        if str(kwargs.get("column_value")):
            return 0
    elif kwargs.get("validation_value") == "int":
        if kwargs.get("column_value").isdigit():
            return 0
    elif kwargs.get("validation_value") == "float":
        if "." in kwargs.get("column_value"):
            float(kwargs.get("column_value"))
            return 0
    elif kwargs.get("validation_value") == "datetime":
        if parser.parse(kwargs.get("column_value")):
            return 0
    elif kwargs.get("validation_value").startswith("datetime."):
        datetime_w_format = kwargs.get("validation_value")
        dot_index = datetime_w_format.find(".") + 1
        fmt = datetime_w_format[dot_index:]
        datetime.strptime(kwargs.get("column_value"), fmt)
        return 0
    return 1


@logging_decorator
def check_column_allow_numeric_value_range(**kwargs):
    """
    validation function checking column value is inside a numeric range
    provided by the list of int values [min value, max value]
    :param kwargs:
    :return:
    """
    if kwargs.get("validation_value")[0] <= \
            float(kwargs.get("column_value")) <= \
            kwargs.get("validation_value")[1]:
        return 0
    return 1


@logging_decorator
def check_column_allow_fixed_value_list(**kwargs):
    """
    validation function checking column value is in a expected list of values
    :param kwargs:
    :return:
    """
    if kwargs.get("column_value") in [str(x) for x in kwargs.get("validation_value")]:
        return 0
    return 1


@logging_decorator
def check_column_allow_fixed_value(**kwargs):
    """
    validation function checking column value is equal to a expected value
    :param kwargs:
    :return:
    """
    if kwargs.get("column_value") == str(kwargs.get("validation_value")):
        return 0
    return 1


@logging_decorator
def check_column_allow_substring(**kwargs):
    """
    validation function checking column value is a substring of a provided string
    :param kwargs:
    :return:
    """
    if kwargs.get("column_value") in kwargs.get("validation_value"):
        return 0
    return 1


@logging_decorator
def check_column_allow_regex(**kwargs):
    """
    validation function checking column value against a provided regex expr.
    :param kwargs:
    :return:
    """
    result = re.match(kwargs.get("validation_value"), kwargs.get("column_value"))

    if result:
        return 0
    return 1
