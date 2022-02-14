from csv_file_validator import validation_functions


class TestsFileLevelValidationFuncs:
    TESTING_KWARGS = {'file_name': 'SalesJan2009_with_header_fixed_sample.csv',
                      'file_row_count': 1000,
                      'file_size': 10,
                      'file_header': [
                          "Transaction_date",
                          "Product",
                          "Price"
                      ]}

    def test_check_file_extension(self):
        TestsFileLevelValidationFuncs.TESTING_KWARGS['validation_value'] = 'csv'
        assert validation_functions.check_file_extension(**TestsFileLevelValidationFuncs.TESTING_KWARGS) == 0

        TestsFileLevelValidationFuncs.TESTING_KWARGS['validation_value'] = 'tsv'
        assert validation_functions.check_file_extension(**TestsFileLevelValidationFuncs.TESTING_KWARGS) == 1

    def test_check_file_mask(self):
        TestsFileLevelValidationFuncs.TESTING_KWARGS['validation_value'] = '.+\\d+'
        assert validation_functions.check_file_mask(**TestsFileLevelValidationFuncs.TESTING_KWARGS) == 0

        TestsFileLevelValidationFuncs.TESTING_KWARGS['validation_value'] = 'd+'
        assert validation_functions.check_file_mask(**TestsFileLevelValidationFuncs.TESTING_KWARGS) == 1

    def test_check_file_size_range(self):
        TestsFileLevelValidationFuncs.TESTING_KWARGS['validation_value'] = [0, 100]
        assert validation_functions.check_file_size_range(**TestsFileLevelValidationFuncs.TESTING_KWARGS) == 0

        TestsFileLevelValidationFuncs.TESTING_KWARGS['validation_value'] = [100, 150]
        assert validation_functions.check_file_size_range(**TestsFileLevelValidationFuncs.TESTING_KWARGS) == 1

    def test_check_file_row_count_range(self):
        TestsFileLevelValidationFuncs.TESTING_KWARGS['validation_value'] = [0, 10000]
        assert validation_functions.check_file_row_count_range(
            **TestsFileLevelValidationFuncs.TESTING_KWARGS) == 0

        TestsFileLevelValidationFuncs.TESTING_KWARGS['validation_value'] = [50, 100]
        assert validation_functions.check_file_row_count_range(
            **TestsFileLevelValidationFuncs.TESTING_KWARGS) == 1

    def test_check_file_header_column_names(self):
        TestsFileLevelValidationFuncs.TESTING_KWARGS['validation_value'] = ["Transaction_date",
                                                                            "Product",
                                                                            "Price"]
        assert validation_functions.check_file_header_column_names(
            **TestsFileLevelValidationFuncs.TESTING_KWARGS) == 0

        TestsFileLevelValidationFuncs.TESTING_KWARGS['validation_value'] = ["wrong_col_name1",
                                                                            "wrong_col_name2",
                                                                            "wrong_col_name3"]
        assert validation_functions.check_file_header_column_names(
            **TestsFileLevelValidationFuncs.TESTING_KWARGS) == 1


class TestLineLevelValidationFuncs:
    TESTING_KWARGS_INT_COLUMN = {'column': 'Price',
                                 'column_value': '1201'}
    TESTING_KWARGS_FLOAT_COLUMN = {'column': 'Price',
                                   'column_value': '12.01'}
    TESTING_KWARGS_STR_COLUMN = {'column': 'Country',
                                 'column_value': 'United States'}

    def test_check_column_allow_data_type(self):
        TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN['validation_value'] = 'int'
        assert validation_functions.check_column_allow_data_type(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN) == 0

        TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN['validation_value'] = 'float'
        assert validation_functions.check_column_allow_data_type(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN) == 1

    def test_check_column_allow_int_value_range(self):
        TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN['validation_value'] = [0, 2000]
        assert validation_functions.check_column_allow_int_value_range(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN) == 0

        TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN['validation_value'] = [5000, 10000]
        assert validation_functions.check_column_allow_int_value_range(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN) == 1

    def test_check_column_allow_float_value_range(self):
        TestLineLevelValidationFuncs.TESTING_KWARGS_FLOAT_COLUMN['validation_value'] = [0.10, 20.15]
        assert validation_functions.check_column_allow_float_value_range(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_FLOAT_COLUMN) == 0

        TestLineLevelValidationFuncs.TESTING_KWARGS_FLOAT_COLUMN['validation_value'] = [-12.55, 10.20]
        assert validation_functions.check_column_allow_float_value_range(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_FLOAT_COLUMN) == 1

    def test_check_column_allow_fixed_value_list(self):
        TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN['validation_value'] = [1201, 1202]
        assert validation_functions.check_column_allow_fixed_value_list(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN) == 0

        TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN['validation_value'] = [3000, 3001]
        assert validation_functions.check_column_allow_fixed_value_list(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN) == 1

    def test_check_column_allow_fixed_value(self):
        TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN['validation_value'] = 1201
        assert validation_functions.check_column_allow_fixed_value(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN) == 0

        TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN['validation_value'] = 9999
        assert validation_functions.check_column_allow_fixed_value(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_INT_COLUMN) == 1

    def test_check_column_allow_substring(self):
        TestLineLevelValidationFuncs.TESTING_KWARGS_STR_COLUMN['validation_value'] = 'xUnited Statesx'
        assert validation_functions.check_column_allow_substring(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_STR_COLUMN) == 0

        TestLineLevelValidationFuncs.TESTING_KWARGS_STR_COLUMN['validation_value'] = 'xxyz'
        assert validation_functions.check_column_allow_substring(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_STR_COLUMN) == 1

    def test_check_column_allow_regex(self):
        TestLineLevelValidationFuncs.TESTING_KWARGS_STR_COLUMN['validation_value'] = '[a-zA-Z].+'
        assert validation_functions.check_column_allow_regex(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_STR_COLUMN) == 0

        TestLineLevelValidationFuncs.TESTING_KWARGS_STR_COLUMN['validation_value'] = '[A-D]'
        assert validation_functions.check_column_allow_regex(
            **TestLineLevelValidationFuncs.TESTING_KWARGS_STR_COLUMN) == 1
