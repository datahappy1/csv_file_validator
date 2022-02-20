"""
file.py
"""
import csv
import os
from collections.abc import Generator
from dataclasses import dataclass
from typing import List, Optional

from csv_file_validator.config import Config
from csv_file_validator.exceptions import InvalidLineColumnCountException


@dataclass
class CsvFileProperties:
    """
    csv file format properties class
    """

    file_row_terminator: str
    file_value_separator: str
    file_value_quote_char: str


def construct_csv_file_properties(config: Config) -> CsvFileProperties:
    """
    construct csv file properties
    :param config:
    :return:
    """
    return CsvFileProperties(
        file_row_terminator=config.file_metadata.file_row_terminator,
        file_value_separator=config.file_metadata.file_value_separator,
        file_value_quote_char=config.file_metadata.file_value_quote_char
    )


def get_csv_reader(file_handle, csv_file_properties: CsvFileProperties):
    """
    get csv reader function
    :param file_handle:
    :param csv_file_properties:
    :return:
    """
    return csv.reader(
        file_handle,
        delimiter=csv_file_properties.file_value_separator,
        quotechar=csv_file_properties.file_value_quote_char,
    )


class File:
    """
    File class
    """

    def __init__(self, config: Config, file_name: str):
        self.config: Config = config
        self.file_name: str = file_name
        self.csv_file_properties: CsvFileProperties = construct_csv_file_properties(self.config)
        self.file_handle = open(file_name, mode="r", encoding="utf8")
        self.file_size: int = int(os.path.getsize(self.file_name) / 1024 / 1024)
        self.file_header: Optional[List[str]] = self._get_file_header()
        self.file_first_row_column_count: int = self.get_first_row_column_count()

    @property
    def file_with_configured_header_has_empty_header(self) -> bool:
        """
        method checking if we can validate the file based on its content
        :return:
        """
        return self.file_header == [""]

    @property
    def file_data_row_count(self) -> int:
        """
        file data row count property
        :return:
        """
        file_data_row_count: int = self._get_rowcount_from_generator()

        if self.file_header and self.file_header != [""]:
            # we subtract 1 from the file_row_count because of the header row
            file_data_row_count -= 1
        return file_data_row_count

    @property
    def file_has_no_data_rows(self) -> bool:
        """
        method checking if the file has any rows (besides header row if configured)
        :return:
        """
        return self.file_data_row_count == 0

    def _get_rowcount_from_generator(self) -> int:
        """
        method to get count of rows from _file_rowcount_generator
        :return:
        """

        def _file_rowcount_generator() -> Generator:
            """
            file row counting generator method
            :return:
            """
            for _ in get_csv_reader(
                file_handle=self.file_handle,
                csv_file_properties=self.csv_file_properties,
            ):
                yield

        row_count: int = len(list(_file_rowcount_generator()))

        self.reset_file_handler()

        return row_count

    def _get_file_header(self) -> list:
        """
        method to get file header row
        :return:
        """
        file_header: Optional[List[str]] = None
        if self.config.file_metadata.file_has_header:
            file_header = (
                self.file_handle.readline()
                    .rstrip(self.csv_file_properties.file_row_terminator)
                    .split(self.csv_file_properties.file_value_separator)
            )

        self.reset_file_handler()

        return file_header

    def get_first_row_column_count(self) -> int:
        """
        method to get the first data row item length for file
        column count integrity check in the file_read_generator method
        :return:
        """
        first_row: List = (
            self.file_handle.readline()
                .rstrip(self.csv_file_properties.file_row_terminator)
                .split(self.csv_file_properties.file_value_separator)
        )

        self.reset_file_handler()

        return len(first_row) if first_row != [""] else 0

    def reset_file_handler(self) -> None:
        """
        method to reset the file handler using seek back to file beginning
        :return:
        """
        self.file_handle.seek(0)

    def close_file_handler(self) -> None:
        """
        method for closing the file handler after validations finished
        :return:
        """
        self.file_handle.close()

    def file_read_generator(self) -> Generator:
        """
        file reading generator method
        :return:
        """
        row_count: int = 0
        for row in get_csv_reader(
            file_handle=self.file_handle,
            csv_file_properties=self.csv_file_properties
        ):
            row_count += 1

            if len(row) != self.file_first_row_column_count:
                raise InvalidLineColumnCountException(
                    f"row #: {row_count}, "
                    f"expected column count: "
                    f"{self.get_first_row_column_count()}, "
                    f"actual column count: "
                    f"{len(row)}"
                )

            if self.file_header and row_count > 1:
                # if file contains header, yield row number and column names with values as dict
                # row number,{'column name 1': 'value', 'column name 2': 'value',..}
                yield row_count, dict(zip(self.file_header, row))
            elif not self.file_header:
                # if file is without header, yield row number and column indexes with values as dict
                # row number,{'0': 'value', '1': 'value',..}
                yield row_count, dict((str(x[0]), x[1]) for x in enumerate(row))
            else:
                # file header row so continue, header should be checked separately in
                # file_validation_rules.file_header_column_names
                continue
