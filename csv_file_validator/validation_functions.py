import os
import re
import sys
import logging
from dateutil import parser

logger = logging.getLogger(__name__)
currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name


def _get_logged_error(func_name, type, **kwargs):
    if type == "file_level":
        logger.error(f'{func_name} - failed on : '
                     f'validation name: {kwargs.get("validation_name")} , '
                     f'validation value: {kwargs.get("validation_value")} ')

    elif type == "column_level":
        logger.error(f'{func_name} - row {kwargs.get("row_number")} failed on : '
                     f'column: {kwargs.get("column")} , '
                     f'column value: {kwargs.get("column_value")} , '
                     f'validation value: {kwargs.get("validation_value")} ')
    else:
        raise NotImplementedError


def check_file_extension(**kwargs):
    if os.path.splitext(kwargs.get('file_name'))[1][1:] == kwargs.get('validation_value'):
        pass
    else:
        _get_logged_error(currentFuncName(), type="file_level", **kwargs)


def check_filemask(**kwargs):
    file = os.path.split(kwargs.get('file_name'))[-1]
    dot_index = file.rfind('.')
    filename = file[:dot_index]
    result = re.match(kwargs.get('validation_value'), filename)

    if result:
        pass
    else:
        _get_logged_error(currentFuncName(), type="file_level", **kwargs)


def check_file_size_range(**kwargs):
    fsize = os.path.getsize(kwargs.get('file_name')) / 1024 / 1024

    if fsize >= kwargs.get('validation_value')[0] and fsize <= kwargs.get('validation_value')[1]:
        pass
    else:
        _get_logged_error(currentFuncName(), type="file_level", **kwargs)


def check_file_row_count_range(**kwargs):
    if kwargs.get('validation_value')[1] >= kwargs.get('file_row_count') >= kwargs.get('validation_value')[0]:
        pass
    else:
        _get_logged_error(currentFuncName(), type="file_level", **kwargs)


def check_file_header_column_names(**kwargs):
    first_line = kwargs.get('file_header')

    if first_line == kwargs.get('file_header'):
        pass
    else:
        _get_logged_error(currentFuncName(), type="file_level", **kwargs)


def check_column_allow_data_type(**kwargs):
    try:
        if kwargs.get("validation_value") == "str":
            str(kwargs.get("column_value"))
        elif kwargs.get("validation_value") == "int":
            int(kwargs.get("column_value"))
        elif kwargs.get("validation_value") == "float":
            float(kwargs.get("column_value"))
        elif kwargs.get("validation_value") == "datetime":
            parser.parse(kwargs.get("column_value"))
        else:
            raise NotImplementedError
    except (TypeError, ValueError):
        _get_logged_error(currentFuncName(), type="column_level", **kwargs)


def check_column_allow_numeric_value_range(**kwargs):
    try:
        int(kwargs.get("column_value"))
    except ValueError:
        logger.error(f'{__name__} row {kwargs.get("idx")} failed with {kwargs}')
        return

    if kwargs.get("validation_value")[0] <= int(kwargs.get("column_value")) <= kwargs.get("validation_value")[1]:
        pass
    else:
        _get_logged_error(currentFuncName(), type="column_level", **kwargs)


def check_column_allow_fixed_value_list(**kwargs):
    if kwargs.get("column_value") in [x for x in kwargs.get("validation_value")]:
        pass
    else:
        _get_logged_error(currentFuncName(), type="column_level", **kwargs)


def check_column_allow_fixed_value(**kwargs):
    if kwargs.get("column_value") == kwargs.get("validation_value"):
        pass
    else:
        _get_logged_error(currentFuncName(), type="column_level", **kwargs)


def check_column_allow_substring(**kwargs):
    if kwargs.get("column_value") in kwargs.get("validation_value"):
        pass
    else:
        _get_logged_error(currentFuncName(), type="column_level", **kwargs)


def check_column_allow_regex(**kwargs):
    result = re.match(kwargs.get('validation_value'), kwargs.get('column_value'))

    # Check if regexp didn't match anything
    if result:
        pass
    else:
        _get_logged_error(currentFuncName(), type="column_level", **kwargs)
