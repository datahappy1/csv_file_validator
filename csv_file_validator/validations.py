import os, re
import logging
from dateutil import parser

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def allow_fixed_value():
    pass


def allow_regex():
    pass


def allow_substring():
    pass


def check_file_extension(**kwargs):
    if os.path.splitext(kwargs.get('file'))[1][1:] == kwargs.get('arg1'):
        logger.info('check_file_extension passed')
    else:
        logger.warning('check_file_extension failed')


def check_filemask(**kwargs):
    file = os.path.split(kwargs.get('file'))[-1]
    dot_index = file.rfind('.')
    filename = file[:dot_index]

    result = re.match(kwargs.get('arg1'), filename)

    # Check if regexp didn't match anything
    if result:
        logger.info('check_filemask passed')
    else:
        logger.warning('check_filemask failed')


def check_file_size_range(**kwargs):
    fsize = os.path.getsize(kwargs.get('file')) / 1024 / 1024

    if fsize >= kwargs.get('arg1')[0] and fsize <= kwargs.get('arg1')[1]:
        logger.info('check_file_size_range passed')
    else:
        logger.warning('check_file_size_range failed')


def check_file_row_count_range(**kwargs):
    #TODO use the generator in __main__
    num_lines = sum(1 for line in open(kwargs.get('file')))

    if num_lines >= kwargs.get('arg1')[0] and num_lines <= kwargs.get('arg1')[1]:
        logger.info('check_file_row_count_range passed')
    else:
        logger.warning('check_file_row_count_range failed')


def check_file_header_column_names(**kwargs):
    #TODO use the generator in __main__
    first_line = [line for line in open(kwargs.get('file'))][0].split(',')

    if first_line == kwargs.get('arg1'):
        logger.info('check_file_header_column_names passed')
    else:
        logger.warning('check_file_header_column_names failed')


def check_column_allow_data_type(**kwargs):
    try:
        if kwargs.get("arg1") == "str":
            str(kwargs.get("arg2"))
            pass
        elif kwargs.get("arg1") == "int":
            int(kwargs.get("arg2"))
            pass
        elif kwargs.get("arg1") == "datetime":
            parser.parse(kwargs.get("arg2"))
            pass
        else:
            raise NotImplementedError
    except (TypeError, ValueError) as e:
        logger.info(f'check_column_allow_data_type failed {kwargs.get("arg1")} - {kwargs.get("arg2")} - {type(kwargs.get("arg2"))} - {e}')


def check_column_allow_numeric_value_range(**kwargs):
    try:
        int(kwargs.get("arg2"))
    except ValueError:
        logger.warning(f'check_column_allow_numeric_value_range failed on casting {kwargs.get("arg2")} to int before validation start')
        return

    if kwargs.get("arg1")[0] <= int(kwargs.get("arg2")) <= kwargs.get("arg1")[1]:
        logger.info('check_column_allow_numeric_value_range passed')
    else:
        logger.warning('check_column_allow_numeric_value_range failed')


def check_column_allow_fixed_value_list(**kwargs):
    if kwargs.get("arg2") in [x for x in kwargs.get("arg1")]:
        logger.info('check_column_allow_fixed_value_list passed')
    else:
        logger.warning('check_column_allow_fixed_value_list failed')


def check_column_allow_fixed_value(**kwargs):
    if kwargs.get("arg2") == kwargs.get("arg1"):
        logger.info('check_column_allow_fixed_value passed')
    else:
        logger.warning('check_column_allow_fixed_value failed')


def check_column_allow_substring(**kwargs):
    if kwargs.get("arg2") in kwargs.get("arg1"):
        logger.info('check_column_allow_substring passed')
    else:
        logger.warning('check_column_allow_substring failed')


def check_column_allow_regex(**kwargs):
    result = re.match(kwargs.get('arg1'), kwargs.get('arg2'))

    # Check if regexp didn't match anything
    if result:
        logger.info('check_column_allow_regex passed')
    else:
        logger.warning('check_column_allow_regex failed')
