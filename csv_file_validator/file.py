"""
file.py
"""
import csv
import os
from collections.abc import Generator
from typing import List, Optional, IO, Iterator

from csv_file_validator.config import Config
from csv_file_validator.exceptions import InvalidLineColumnCountException


class CsvProperties:
    """
    csv file format properties class
    """

    def __init__(self, config: Config):
        self.file_row_terminator: str = config.file_metadata.file_row_terminator
        self.file_value_separator: str = config.file_metadata.file_value_separator
        self.file_value_quote_char: str = config.file_metadata.file_value_quote_char


class File:
    """
    File class
    """

    def __init__(self, config: Config, file_name: str):
        self.config: Config = config
        self.name: str = file_name
        self.csv_properties: CsvProperties = CsvProperties(config=self.config)
        self.handle: IO = open(file_name, mode="r", encoding="utf8")
        self.size: int = int(os.path.getsize(self.name) / 1024 / 1024)
        self.header: Optional[List[str]] = self._get_file_header()
        self.file_first_row_column_count: int = self.get_first_row_column_count()

    @property
    def with_configured_header_has_empty_header(self) -> bool:
        """
        file with configured header has empty header property
        :return:
        """
        return self.header == [""]

    @property
    def data_row_count(self) -> int:
        """
        file data row count property
        :return:
        """
        file_data_row_count: int = self._get_rowcount_from_generator()

        if self.header and self.header != [""]:
            # we subtract 1 from the file_row_count because of the header row
            file_data_row_count -= 1
        return file_data_row_count

    @property
    def has_no_data_rows(self) -> bool:
        """
        property method checking if the file has any rows (besides header row if configured)
        :return:
        """
        return self.data_row_count == 0

    def _reset_file_handler(self) -> None:
        """
        method to reset the file handler using seek back to file beginning
        :return:
        """
        self.handle.seek(0)

    def _get_csv_reader(self) -> Iterator:
        """
        method to get csv reader
        :return:
        """
        return csv.reader(
            self.handle,
            delimiter=self.csv_properties.file_value_separator,
            quotechar=self.csv_properties.file_value_quote_char,
        )

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
            for _ in self._get_csv_reader():
                yield

        row_count: int = len(list(_file_rowcount_generator()))

        self._reset_file_handler()

        return row_count

    def _get_file_header(self) -> list:
        """
        method to get file header row
        :return:
        """
        file_header: Optional[List[str]] = None
        if self.config.file_metadata.file_has_header:
            file_header = (
                self.handle.readline()
                .rstrip(self.csv_properties.file_row_terminator)
                .split(self.csv_properties.file_value_separator)
            )

        self._reset_file_handler()

        return file_header

    def get_first_row_column_count(self) -> int:
        """
        method to get the first data row item length for file
        column count integrity check in the file_read_generator method
        :return:
        """
        first_row: List = (
            self.handle.readline()
            .rstrip(self.csv_properties.file_row_terminator)
            .split(self.csv_properties.file_value_separator)
        )

        self._reset_file_handler()

        return len(first_row) if first_row != [""] else 0

    def close_file_handler(self) -> None:
        """
        method for closing the file handler after validations finished
        :return:
        """
        self.handle.close()

    def file_read_generator(self) -> Generator:
        """
        file reading generator method
        :return:
        """
        row_count: int = 0
        for row in self._get_csv_reader():
            row_count += 1

            if len(row) != self.file_first_row_column_count:
                raise InvalidLineColumnCountException(
                    f"row #: {row_count}, "
                    f"expected column count: "
                    f"{self.get_first_row_column_count()}, "
                    f"actual column count: "
                    f"{len(row)}"
                )

            if self.header and row_count > 1:
                # if file contains header, yield row number and column names with values as dict
                # row number,{'column name 1': 'value', 'column name 2': 'value',..}
                yield row_count, dict(zip(self.header, row))
            elif not self.header:
                # if file is without header, yield row number and column indexes with values as dict
                # row number,{'0': 'value', '1': 'value',..}
                yield row_count, dict((str(x[0]), x[1]) for x in enumerate(row))
            else:
                # file header row so continue, header should be checked separately in
                # file_validation_rules.file_header_column_names
                continue
