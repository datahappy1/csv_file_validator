import platform
from types import SimpleNamespace, FunctionType
from csv_file_validator import validations

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
        'file_value_separator': ',',
        'file_has_header': True,
        'file_header_column_names': ['col1', 'col2', 'col3'],
        'column_datatypes': {
            'col1': 'str',
            'col2': 'str',
            'col3': 'str'
        },
        'column_validation_rules': {
            'col1': {
                'allow_numeric_value_range': [0, 100]
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


class Validate:
    def __init__(self, config):
        self.config = config

    def _get_config(self):
        if isinstance(self.config, dict):
            return SimpleNamespace(**self.config)
        else:
            raise

    def _get_high_severity_validations(self):
        return {k: v for k, v in self.config.get('high_severity_validations').items()}

    def _get_low_severity_validations(self):
        return {k: v for k, v in self.config.get('low_severity_validations').items()}

    def _get_all_severity_validations(self):
        return {**self._get_high_severity_validations(), **self._get_low_severity_validations()}

    def _get_validation(self, validation_rule):
        return {k: v for k, v in self._get_all_severity_validations().items() if k == validation_rule}

    def _instantiate_validation(self):
        for k, v in self._get_all_severity_validations().items():
            setattr(self, k, v)

    def read_file(self):
        data = pd.read_csv("test1.csv",
                           dtype=self.config.get('low_severity_validations').get('column_datatypes'),
                           sep=self.config.get('low_severity_validations').get('file_value_separator'),
                           header=1,
                           engine="c")

        print(data)


vobj = Validate(config)
Validate.read_file(vobj)
print(Validate._get_high_severity_validations(vobj))
print(Validate._get_low_severity_validations(vobj))
print(Validate._get_all_severity_validations(vobj))
print(Validate._get_validation(vobj, validation_rule="file_has_header"))
print(Validate._instantiate_validation(vobj))
Validate.allow_numeric_range_value()
