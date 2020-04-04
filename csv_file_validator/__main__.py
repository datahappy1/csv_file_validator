import logging
from csv_file_validator.validation import SetupValidation, ValidateFile

# set logging levels for main function console output
logging_level=logging.DEBUG
logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)


FILEPATH = ["SalesJan2009.csv"]
CONFIG = {
    'file_metadata': {
        'file_value_separator': ',',
        'file_row_terminator': '\n',
        'file_has_header': True,
    },
    'file_validation_rules': {
        'file_name_file_mask': 'SalesJ',
        'file_extension': 'csv',
        'file_size_range': [0, 1],
        'file_row_count_range': [0, 1000],
        'file_header_column_names': ['Transaction_date', 'Product', 'Price', 'Payment_Type', 'Name', 'City', 'State',
                                     'Country', 'Account_Created', 'Last_Login', 'Latitude', 'Longitude']
    },
    'column_validation_rules': {
        'Transaction_date': {
            'allow_data_type': 'datetime',
        },
        'Country': {
            'allow_fixed_value_list': ['yyy', 'www'],
            'allow_regex': '$#%@%^@',
            'allow_data_type': 'str'
        },
        'Price': {
            'allow_numeric_value_range': [0, 100000],
            'allow_substring': 'xxzerw',
            'allow_fixed_value': 'xxx',
            'allow_data_type': 'int'
        }
    }
}

if __name__ == '__main__':

    for file in FILEPATH:

        logger.info(f'Validation of {file} started')

        validation_obj = SetupValidation(CONFIG)
        validate_config = validation_obj.get_validated_config()
        validation_file_obj = ValidateFile(CONFIG, file)

        logger.info(f'Evaluation of file validation rules started')
        validation_file_obj.validate_file()
        logger.info(f'Evaluation of file validation rules finished')

        logger.info(f'Evaluation of column validation rules started')
        for idx,line in enumerate(validation_file_obj.file_read_generator()):
            ValidateFile.validate_line(validation_file_obj, line, idx)
        logger.info(f'Evaluation of column validation rules finished')

        ValidateFile.close_file_handler(validation_file_obj)

        logger.info(f'Validation of {file} finished')
