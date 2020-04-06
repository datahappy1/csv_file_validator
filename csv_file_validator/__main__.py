import logging
import argparse
from csv_file_validator.validation import SetupValidation, ValidateFile, InvalidLineColumnCountException

# set logging levels for main function console output
logging_level = logging.DEBUG
logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)

FILEPATH = ["SalesJan2009_no_header.csv", "SalesJan2009_no_header_fixed.csv"]
CONFIG = {
    'file_metadata': {
        'file_value_separator': ',',
        'file_row_terminator': '\n',
        'file_has_header': False,
    },
    'file_validation_rules': {
        'file_name_file_mask': 'SalesJ',
        'file_extension': 'csv',
        'file_size_range': [0, 1],
        'file_row_count_range': [0, 1000],
        # 'file_header_column_names': ['Transaction_date', 'Product', 'Price', 'Payment_Type', 'Name', 'City', 'State',
        #                              'Country', 'Account_Created', 'Last_Login', 'Latitude', 'Longitude']
    },
    'column_validation_rules': {
        0: {
            'allow_data_type': 'datetime',
        },
        1: {
            # 'allow_fixed_value_list': ['Norway', 'www'],
            # 'allow_regex': '$#%@%^@',
            # 'allow_substring': '',
            'allow_data_type': 'str'
        },
        2: {
            'allow_numeric_value_range': [0, 100000],
            # 'allow_fixed_value': '1000',
            'allow_data_type': 'int'
            # 'Transaction_date': {
            #     'allow_data_type': 'datetime',
            # },
            # 'Country': {
            #     # 'allow_fixed_value_list': ['Norway', 'www'],
            #     # 'allow_regex': '$#%@%^@',
            #     # 'allow_substring': '',
            #     'allow_data_type': 'str'
            # },
            # 'Price': {
            #     'allow_numeric_value_range': [0, 100000],
            #     # 'allow_fixed_value': '1000',
            #     'allow_data_type': 'int'
        }
    }
}


def validation_runner(file, config):
    logger.info(f'Validation of {file} started')

    validation_obj = SetupValidation(config)
    validation_obj.get_validated_config()

    logger.info(f'Validation config initiated and validated')

    validation_file_obj = ValidateFile(config, file)

    logger.info(f'Evaluation of file validation rules starting')

    file_level_validations_counter, file_level_failed_validations_counter = validation_file_obj.validate_file()

    logger.info(f'Evaluation of {file_level_validations_counter} file validation rules finished')

    logger.info(f'Evaluation of column validation rules starting')

    column_level_validations_counter = 0
    column_level_failed_validations_counter = 0
    try:
        for idx, line in enumerate(validation_file_obj.file_read_generator()):
            _all_validations_count, _all_failed_validations_counter = ValidateFile.validate_line(validation_file_obj,
                                                                                                 line, idx)
            column_level_validations_counter += _all_validations_count
            column_level_failed_validations_counter += _all_failed_validations_counter

        logger.info(f'Evaluation of {column_level_validations_counter} column validation rules finished')
        logger.info(f'Validation of {file} finished with: '
                    f'{file_level_failed_validations_counter} failed file level validations ,'
                    f'{column_level_failed_validations_counter} failed column level validations')

    except InvalidLineColumnCountException as ColCountErr:
        logger.error(f'File cannot be validated, column count is not consistent {ColCountErr}')

    ValidateFile.close_file_handler(validation_file_obj)


def prepare_args():
    """
    function for preparation of the CLI arguments
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-fl', '--filelocation', type=str, required=True)
    parser.add_argument('-config', '--configfile', type=str, required=True)
    parsed = parser.parse_args()

    file = parsed.filelocation
    config = parsed.configfile

    # verify the source file location is a valid file and folder

    # load the config file to dict in case it's a filepath
    # do the same if it's a json

    return {'file': file,
            'config': config}


if __name__ == '__main__':

    # prepared_args = prepare_args()
    # main_result = main(**prepared_args)

    for file in FILEPATH:
        validation_runner(file, CONFIG)
