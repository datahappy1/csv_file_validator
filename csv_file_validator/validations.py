import os, re

def file_name_filemask(file_name):
    pass


def file_extension(file_extension):
    pass


def file_size_range(file_size):
    pass


def file_value_separator():
    pass


def row_count_range(df):
    pass


def file_has_header():
    pass


def file_header_column_names():
    pass


def file_column_datatypes():
    pass


def allow_numeric_value_range():
    pass


def allow_fixed_value():
    pass


def allow_fixed_value_list():
    pass


def allow_regex():
    pass


def allow_substring():
    pass


def check_file_extension(**kwargs) -> bool:
    """
    checks the file extension matches value in validation_schema
    """
    # rfind() returns -1 if it doesn't find the character it's looking for
    # if self.file.rfind('.') >= 0:
    #     dot_index = self.file.rfind('.')
    #     result = self.file[dot_index + 1:] == file_extension
    #     return result
    # else:
    #     result = file_extension == ''
    #     return result
    return kwargs.items()

def check_filemask(**kwargs) -> bool:
    """
    checks the filename matches the regex pattern stipulated in the
    validation_schema
    """

    # file = os.path.split(self.file)[-1]
    # dot_index = file.rfind('.')
    # filename = file[:dot_index]
    # result = re.match(filemask, filename)
    #
    # # Check if regexp didn't match anything
    # if result is None:
    #     return False
    # else:
    #     return True
    print(kwargs)
    return kwargs.items()
