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


class ValidationErrorException(Exception):
    """
    Validation error Exception custom exception type
    """
