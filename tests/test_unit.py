from csv_file_validator import validation_functions


# class TestValidation:
#     def test_function_caller(self):
#         pass
#
#     def test_validate_config_file(self):
#         pass
#
#     def test_get_validated_config(self):
#         pass
#
#     def test_get_config_file_metadata_items(self):
#         pass
#
#     def test_get_config_file_metadata_value(self):
#         pass
#
#     def test_get_config_file_validation_rules_items(self):
#         pass
#
#     def test_get_config_column_validation_rules_items(self):
#         pass
#
#     def test_file_read_generator(self):
#         pass
#
#     def test_close_file_handler(self):
#         pass
#
#     def test_validate_file(self):
#         pass
#
#     def test_validate_line(self):
#         pass


class TestsFileLevelValidationFuncs:
    def test_check_file_extension(self):
        assert validation_functions.check_file_extension(**self.positive_testing_kwargs) == 0
        assert validation_functions.check_file_extension(**self.negative_testing_kwargs) == 1

    def test_check_file_mask(self):
        assert validation_functions.check_file_mask(**self.positive_testing_kwargs) == 0
        assert validation_functions.check_file_mask(**self.negative_testing_kwargs) == 1

    def test_check_file_size_range(self):
        assert validation_functions.check_file_size_range(**self.positive_testing_kwargs) == 0
        assert validation_functions.check_file_size_range(**self.negative_testing_kwargs) == 1

    def test_check_file_row_count_range(self):
        assert validation_functions.check_file_row_count_range(**self.positive_testing_kwargs) == 0
        assert validation_functions.check_file_row_count_range(**self.negative_testing_kwargs) == 1

    def test_check_file_header_column_names(self):
        assert validation_functions.check_file_header_column_names(**self.positive_testing_kwargs) == 0
        assert validation_functions.check_file_header_column_names(**self.negative_testing_kwargs) == 1


class TestLineLevelValidationFuncs:
    def test_check_column_allow_data_type(self):
        assert validation_functions.check_column_allow_data_type(**self.positive_testing_kwargs) == 0
        assert validation_functions.check_column_allow_data_type(**self.negative_testing_kwargs) == 1

    def test_check_column_allow_numeric_value_range(self):
        assert validation_functions.check_column_allow_numeric_value_range(**self.positive_testing_kwargs) == 0
        assert validation_functions.check_column_allow_numeric_value_range(**self.negative_testing_kwargs) == 1

    def test_check_column_allow_fixed_value_list(self):
        assert validation_functions.check_column_allow_fixed_value_list(**self.positive_testing_kwargs) == 0
        assert validation_functions.check_column_allow_fixed_value_list(**self.negative_testing_kwargs) == 1

    def test_check_column_allow_fixed_value(self):
        assert validation_functions.check_column_allow_fixed_value(**self.positive_testing_kwargs) == 0
        assert validation_functions.check_column_allow_fixed_value(**self.negative_testing_kwargs) == 1

    def test_check_column_allow_substring(self):
        assert validation_functions.check_column_allow_substring(**self.positive_testing_kwargs) == 0
        assert validation_functions.check_column_allow_substring(**self.negative_testing_kwargs) == 1

    def test_check_column_allow_regex(self):
        assert validation_functions.check_column_allow_regex(**self.positive_testing_kwargs) == 0
        assert validation_functions.check_column_allow_regex(**self.negative_testing_kwargs) == 1
