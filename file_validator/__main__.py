import platform

pf = platform.system()

if pf == 'linux':
    import modin.pandas as pd
else:
    import pandas as pd

# basicdtypes  float, int, bool, timedelta64[ns] and datetime64[ns], string
# https://pandas.pydata.org/pandas-docs/stable/getting_started/basics.html#basics-dtypes
# config
config = {
    'high_severity_validations': {
        'file_name_filemask': 'test*',
        'file_extension': 'csv',
        'file_size_range': [0, 1],
        'file_row_count_range': [0, 50],
    },
    'low_severity_validations': {
        'file_has_header': True,
        'file_header_column_names': ['col1', 'col2', 'col3'],
        'column_datatypes': {
            'col1': 'str',
            'col2': 'str',
            'col3': 'str'
        },
        'column_validation_rules': {
            'col1': {
                'allow_fixed_value_list': ['xxx', 'yyy']
            },
            'col2': {
                'allow_fixed_value_list': ['yyy', 'www'],
                'allow_regex': '$#%@%^@',
            },
            'col3': {
                'allow_substring': 'xxzerw',
                'allow_fixed_value': 'xxx'
            }
        }
    }
}


def file_name_filemask(file_name):
    pass


def file_extension(file_extension):
    pass


def file_size_range(file_size):
    pass


def row_count_range(df):
    pass


def file_has_header():
    pass


def file_header_column_names():
    pass


def column_datatypes():
    pass


def allow_fixed_value():
    pass


def allow_fixed_value_list():
    pass


def allow_regex():
    pass


def allow_substring():
    pass


data = pd.read_csv("test1.csv",
                   dtype=config.get('column_datatypes'),
                   sep=",",
                   header=1,
                   engine="c")

print(data)
