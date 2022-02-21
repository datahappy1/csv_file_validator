"""
settings parser
"""
from configparser import ConfigParser
from dataclasses import dataclass

from csv_file_validator.exceptions import InvalidSettingsException


@dataclass
class Settings:
    """
    settings class
    """

    skip_column_validations_on_empty_file: bool
    raise_exception_and_halt_on_failed_validation: bool


def prepare_settings(settings_file_loc="settings.conf") -> Settings:
    """
    function for parsing values from settings.conf
    :param settings_file_loc:
    :return:
    """
    settings: dict = dict()

    parser: ConfigParser = ConfigParser()
    parser.read(settings_file_loc)

    if not parser.has_section("project_scoped_settings"):
        raise InvalidSettingsException(
            "missing project_scoped_settings section in settings.conf"
        )

    if not parser.has_option(
        "project_scoped_settings", "SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE"
    ):
        raise InvalidSettingsException(
            "missing SKIP_COLUMN_VALIDATIONS_ON_EMPTY_FILE option "
            "in the section project_scoped_settings in settings.conf"
        )

    if not parser.has_option(
        "project_scoped_settings", "RAISE_EXCEPTION_AND_HALT_ON_FAILED_VALIDATION"
    ):
        raise InvalidSettingsException(
            "missing RAISE_EXCEPTION_AND_HALT_ON_FAILED_VALIDATION option "
            "in the section project_scoped_settings in settings.conf"
        )

    for name, value in parser.items("project_scoped_settings"):
        if value in ("True", "true"):
            settings[name] = True
        elif value in ("False", "false"):
            settings[name] = False
        else:
            settings[name] = value

    if settings["skip_column_validations_on_empty_file"] not in (True, False):
        settings["skip_column_validations_on_empty_file"] = False

    if settings["raise_exception_and_halt_on_failed_validation"] not in (True, False):
        settings["raise_exception_and_halt_on_failed_validation"] = False

    return Settings(**settings)
