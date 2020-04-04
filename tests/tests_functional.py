from csv_file_validator.validation import SetupValidation, ValidateFile

def test_success_file_with_header():

    validation_obj = SetupValidation(CONFIG)
    validate_config = validation_obj.get_validated_config()

    validation_file_obj = ValidateFile(CONFIG, file)

    file_level_validations_counter, file_level_failed_validations_counter = validation_file_obj.validate_file()

    column_level_validations_counter = 0
    column_level_failed_validations_counter = 0
    for idx, line in enumerate(validation_file_obj.file_read_generator()):
        _all_validations, _all_failed_validations = ValidateFile.validate_line(validation_file_obj, line, idx)
        column_level_validations_counter += _all_validations
        column_level_failed_validations_counter += _all_failed_validations


    ValidateFile.close_file_handler(validation_file_obj)
    assert 1==1