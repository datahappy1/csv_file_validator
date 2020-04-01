import os, re
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)



def allow_fixed_value():
    pass


def allow_fixed_value_list():
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
    if isinstance(kwargs.get(''))
