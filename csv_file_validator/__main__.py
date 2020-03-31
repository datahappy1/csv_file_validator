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

type_to_pd_dtype = {
    "string": "object",
    "integer": "int64",
    "float": "float64",
    "bool": "bool",
    "datetime": "datetime64",
}

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
            type(k, v)

    def read_file(self):
        data = pd.read_csv("test1.csv",
                           dtype=self.config.get('low_severity_validations').get('column_datatypes'),
                           sep=self.config.get('low_severity_validations').get('file_value_separator'),
                           header=1,
                           engine="c")

        print(data)

    def method_caller(self, attribute):
        """
        method to invoke all checks
        """

        attribute_func_map = {
            "file_extension": self.check_file_extension,
            "filemask": self.check_filemask,
            "no_of_columns": self.check_no_of_columns,
            "no_of_rows": self.check_no_of_rows,
            "row_range": self.check_row_range,
            "column_range": self.check_column_range,
            "duplicate_values": self.check_dups_values_allowed,
            "duplicate_rows": self.check_dups_rows_allowed,
            "column_dtypes": self.check_column_dtypes,
            "column_regex": self.check_column_regex,
            "null_values_forbidden_blanket_ban": self.null_val_forbid_blank_ban,
            "null_values_forbidden_columnar": self.null_values_forbid_column,
            "column_value_range": self.check_column_value_range,
            "sql_column_lookup": self.check_sql_column_lookup,
            "customer_check": self.check_ssn_person_svc
        }

        if attribute in attribute_func_map.keys():
            return attribute_func_map[attribute]
        else:
            return None

    def check_file_extension(self, file_extension) -> bool:
        """
        checks the file extension matches value in validation_schema
        """
        # rfind() returns -1 if it doesn't find the character it's looking for
        if self.file.rfind('.') >= 0:
            dot_index = self.file.rfind('.')
            result = self.file[dot_index + 1:] == file_extension
            return result
        else:
            result = file_extension == ''
            return result

    def check_filemask(self, filemask) -> bool:
        """
        checks the filename matches the regex pattern stipulated in the
        validation_schema
        """

        file = os.path.split(self.file)[-1]
        dot_index = file.rfind('.')
        filename = file[:dot_index]
        result = re.match(filemask, filename)

        # Check if regexp didn't match anything
        if result is None:
            return False

        return result and result.span()[1] == len(filename)

vobj = Validate(config)
Validate.read_file(vobj)
print(Validate._get_high_severity_validations(vobj))
print(Validate._get_low_severity_validations(vobj))
print(Validate._get_all_severity_validations(vobj))
print(Validate._get_validation(vobj, validation_rule="file_has_header"))
print(Validate._instantiate_validation(vobj))
Validate.column_validation_rules()
