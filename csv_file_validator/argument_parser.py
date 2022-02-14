"""
argument parser
"""
import json
import os
from argparse import ArgumentParser

from csv_file_validator.exceptions import (
    InvalidFileLocationException,
    InvalidConfigException,
)


def prepare_args() -> dict:
    """
    function for preparation of the CLI arguments
    :return:
    """
    args = dict()

    parser = ArgumentParser()
    parser.add_argument("-fl", "--filelocation", type=str, required=True)
    parser.add_argument("-cfg", "--configfile", type=str, required=True)
    parsed = parser.parse_args()

    parsed_file_loc = parsed.filelocation
    parsed_file_loc_list = []

    if os.path.isdir(parsed_file_loc):
        for path in os.listdir(parsed_file_loc):
            full_path = os.path.join(parsed_file_loc, path)
            if os.path.isfile(full_path):
                parsed_file_loc_list.append(full_path)
        if not parsed_file_loc_list:
            raise InvalidFileLocationException(f"Folder {parsed_file_loc} is empty")

    elif os.path.isfile(parsed_file_loc):
        parsed_file_loc_list = [parsed_file_loc]
    else:
        raise InvalidFileLocationException(
            f"Could not load file(s) {parsed_file_loc} " f"for validation"
        )
    args["file_loc"] = parsed_file_loc_list

    parsed_config = parsed.configfile
    parsed_config_dict = None

    if os.path.isfile(parsed_config):
        with open(parsed_config, mode="r") as json_file:
            try:
                parsed_config_dict = json.load(json_file)
            except json.JSONDecodeError as json_decode_err:
                raise InvalidConfigException(
                    f"Could not load config - valid file, "
                    f"JSON decode error: {json_decode_err}"
                )
            except Exception as exc:
                raise InvalidConfigException(
                    f"Could not load config - valid file, " f"general exception: {exc}"
                )
    else:
        raise InvalidConfigException("Could not load config file - not a valid file")

    args["config"] = parsed_config_dict

    return args
