"""
validation_functions module
"""
import functools
import logging
import os
import re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Optional, Union

from dateutil import parser

from csv_file_validator.exceptions import InvalidConfigException

logger = logging.getLogger(__name__)


def _log_validation_error(func_name: str, **kwargs) -> None:
    """
    function responsible for handling the logging of the failed validations
    :param func_name:
    :param type:
    :param kwargs:
    :return:
    """

    logged_string: str = (
        f'{func_name} - failed to meet this value : {kwargs.get("validation_value")}'
    )

    if kwargs.get("row_number"):
        logged_string += f' - Row#: {kwargs["row_number"]}'
    if kwargs.get("column"):
        logged_string += f' - Column name: {kwargs["column"]}'
    if kwargs.get("column_value"):
        logged_string += f' - Column value: {kwargs["column_value"]}'
    if kwargs.get("Exception"):
        logged_string += f' - Exception: {kwargs["Exception"]}'

    logger.error(logged_string)


def logging_decorator(func):
    """
    logging decorator for validation functions
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper_decorator(**kwargs):
        try:
            validation_result: int = func(**kwargs)
        except (
            ValueError,
            TypeError,
            KeyError,
            IndexError,
            AttributeError,
            ArithmeticError,
        ) as err:
            # in case validation function raised Error,
            # still need to add one more failed validation
            # for the __main__ error counter
            validation_result = 1
            kwargs["Exception"] = err
        except Exception as exc:
            raise RuntimeError(f"Unexpected Exception {exc} in {func.__name__}")

        if validation_result != 0:
            _log_validation_error(func_name=func.__name__, **kwargs)

        return validation_result

    return wrapper_decorator


@logging_decorator
def check_file_extension(**kwargs) -> int:
    """
    validation function checking the file extension is equal to the expected value
    :param kwargs:
    :return:
    """
    if os.path.splitext(kwargs.get("file_name"))[1][1:] == kwargs.get(
        "validation_value"
    ):
        return 0
    return 1


@logging_decorator
def check_file_mask(**kwargs) -> int:
    """
    validation function checking the file name file mask against a provided regex expr.
    :param kwargs:
    :return:
    """
    full_path_file_name: str = os.path.split(kwargs.get("file_name"))[-1]
    dot_index: int = full_path_file_name.rfind(".")
    filename: str = full_path_file_name[:dot_index]

    if re.match(kwargs.get("validation_value"), filename):
        return 0
    return 1


@logging_decorator
def check_file_size_range(**kwargs) -> int:
    """
    validation function checking file size in MB is inside a numeric range
    provided by the list of int values [min value, max value]
    :param kwargs:
    :return:
    """
    if (
        kwargs.get("validation_value")[1]
        >= kwargs.get("file_size")
        >= kwargs.get("validation_value")[0]
    ):
        return 0
    return 1


@logging_decorator
def check_file_row_count_range(**kwargs) -> int:
    """
    validation function checking file row count is inside a numeric range
    provided by the list of int values [min value, max value]
    :param kwargs:
    :return:
    """
    if (
        kwargs.get("validation_value")[0]
        <= kwargs.get("file_row_count")
        <= kwargs.get("validation_value")[1]
    ):
        return 0
    return 1


@logging_decorator
def check_file_header_column_names(**kwargs) -> int:
    """
    validation function checking file header row is equal to the expected header row
    :param kwargs:
    :return:
    """
    if kwargs.get("validation_value") == kwargs.get("file_header"):
        return 0
    return 1


@logging_decorator
def check_column_allow_data_type(**kwargs) -> int:
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
def check_column_allow_int_value_range(**kwargs) -> int:
    """
    validation function checking column value is inside a integer value range
    provided by the list of int values [min value, max value]
    :param kwargs:
    :return:
    """
    if (
        kwargs.get("validation_value")[0]
        <= int(kwargs.get("column_value"))
        <= kwargs.get("validation_value")[1]
    ):
        return 0
    return 1


@logging_decorator
def check_column_allow_float_value_range(**kwargs) -> int:
    """
    validation function checking column value is inside a float value range
    provided by the list of float values [min value, max value]
    :param kwargs:
    :return:
    """
    lower_range: Decimal = Decimal(kwargs.get("validation_value")[0]).quantize(
        Decimal(".01"), rounding=ROUND_HALF_EVEN
    )
    upper_range: Decimal = Decimal(kwargs.get("validation_value")[1]).quantize(
        Decimal(".01"), rounding=ROUND_HALF_EVEN
    )
    column_value: Decimal = Decimal(kwargs.get("column_value")).quantize(
        Decimal(".01"), rounding=ROUND_HALF_EVEN
    )

    if lower_range.compare(column_value) < 0 < upper_range.compare(column_value):
        return 0
    return 1


@logging_decorator
def check_column_allow_fixed_value_list(**kwargs) -> int:
    """
    validation function checking column value is in a expected list of values
    :param kwargs:
    :return:
    """
    if kwargs.get("column_value") in [str(x) for x in kwargs.get("validation_value")]:
        return 0
    return 1


@logging_decorator
def check_column_allow_fixed_value(**kwargs) -> int:
    """
    validation function checking column value is equal to a expected value
    :param kwargs:
    :return:
    """
    if kwargs.get("column_value") == str(kwargs.get("validation_value")):
        return 0
    return 1


@logging_decorator
def check_column_allow_substring(**kwargs) -> int:
    """
    validation function checking column value is a substring of a provided string
    :param kwargs:
    :return:
    """
    if kwargs.get("column_value") in str(kwargs.get("validation_value")):
        return 0
    return 1


@logging_decorator
def check_column_allow_regex(**kwargs) -> int:
    """
    validation function checking column value against a provided regex expr.
    :param kwargs:
    :return:
    """
    if re.match(kwargs.get("validation_value"), kwargs.get("column_value")):
        return 0
    return 1


def execute_mapped_validation_function(attribute, **kwargs):
    """
    mapping method between config rules and validation functions
    :param attribute:
    :param kwargs:
    :return:
    """
    for func_name, func in _ATTRIBUTE_FUNC_MAP.items():
        if func_name == attribute:
            return_value: Optional[Union[str, bool]] = func(**kwargs)
            break
    else:
        raise InvalidConfigException(
            f"function {attribute} not found in " f"function_caller attribute_func_map"
        )
    return return_value


_ATTRIBUTE_FUNC_MAP: dict = {
    "file_name_file_mask": check_file_mask,
    "file_extension": check_file_extension,
    "file_size_range": check_file_size_range,
    "file_row_count_range": check_file_row_count_range,
    "file_header_column_names": check_file_header_column_names,
    "allow_data_type": check_column_allow_data_type,
    "allow_int_value_range": check_column_allow_int_value_range,
    "allow_float_value_range": check_column_allow_float_value_range,
    "allow_fixed_value_list": check_column_allow_fixed_value_list,
    "allow_regex": check_column_allow_regex,
    "allow_substring": check_column_allow_substring,
    "allow_fixed_value": check_column_allow_fixed_value,
}
