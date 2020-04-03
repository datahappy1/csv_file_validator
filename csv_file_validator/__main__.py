import logging
from csv_file_validator.validation import Validate, ValidateFile#, ValidateLine

logger = logging.getLogger(__name__)

ARG1 = ["SalesJan2009.csv"]
ARG2 = config = {
        'file_metadata': {
            'file_value_separator': ',',
            'file_has_header': True,
        },
        'file_validation_rules': {
            'file_name_file_mask': 'SalesJ',
            'file_extension': 'csv',
            'file_size_range': [0, 1],
            'file_row_count_range': [0, 1000],
            'file_header_column_names': ['Transaction_date', 'Product', 'Price', 'Payment_Type', 'Name', 'City', 'State', 'Country', 'Account_Created', 'Last_Login', 'Latitude', 'Longitude']
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

    logger.info('started')
    validation_obj = Validate(ARG2)

    for file in ARG1:
        validation_file_obj = ValidateFile(file)
        validation_file_obj.validate_file()

        # for line in validation_file_obj.file_read_generator():
        #     validation_line_obj = ValidateLine(validation_obj, line)
        #     validation_line_obj.validate_line()

