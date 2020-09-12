"""
exceptions module
"""


class InvalidSettingsException(Exception):
    """
    Invalid settings Exception custom exception type
    """


class InvalidFileLocationException(Exception):
    """
    Invalid file location Exception custom exception type
    """


class InvalidConfigException(Exception):
    """
    Invalid configuration file Exception custom exception type
    """


class InvalidLineColumnCountException(Exception):
    """
    Invalid Line Column Count Exception custom exception type
    """


class FoundValidationErrorException(Exception):
    """
    Found validation error Exception custom exception type
    """


class FoundValidationErrorsException(Exception):
    """
    Found validation errors Exception custom exception type
    """
