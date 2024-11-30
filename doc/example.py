from __future__ import annotations

import enum
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Union

from pysqlsync.model.key_types import PrimaryKey, Unique
from strong_typing.core import JsonType, Schema

if sys.version_info > (3, 10):
    SimpleType = bool | int | float | str
else:
    SimpleType = Union[bool, int, float, str]


@enum.unique
class EnumType(enum.Enum):
    active = "active"
    disabled = "disabled"


class MyException(Exception):
    """
    A custom exception type.
    """


class PlainClass:
    """
    A plain class.

    :param timestamp: A member variable of type `datetime`.
    """

    timestamp: datetime


@dataclass
class SampleClass:
    """
    A data-class with several member variables.

    :param boolean: A member variable of type `bool`.
    :param integer: A member variable of type `int`.
    :param double: A member variable of type `float`.
    :param string: A member variable of type `str`.
    :param enumeration: A member variable with an enumeration type.
    """

    boolean: bool
    integer: int
    double: float
    string: str
    enumeration: EnumType

    def __lt__(self, other: "SampleClass") -> bool:
        "A custom implementation for *less than*."

        return self.integer < other.integer

    def __le__(self, other: "SampleClass") -> bool:
        "A custom implementation for *less than or equal*."

        return self.integer <= other.integer

    def __ge__(self, other: "SampleClass") -> bool:
        "A custom implementation for *greater than or equal*."

        return self.integer >= other.integer

    def __gt__(self, other: "SampleClass") -> bool:
        "A custom implementation for *greater than*."

        return self.integer > other.integer

    def to_json(self) -> JsonType:
        """
        Serializes the data to JSON.

        :returns: A JSON object.
        """
        ...

    @staticmethod
    def from_json(obj: JsonType) -> "SampleClass":
        """
        De-serializes the data from JSON.

        :param obj: A JSON object.
        :returns: An instance of this class.
        """
        ...


@dataclass
class DerivedClass(SampleClass):
    """
    This data-class derives from another base class.

    :param union: A union of several types.
    :param json: A complex type with type substitution.
    :param schema: A complex type without type substitution.
    """

    union: SimpleType
    json: JsonType
    schema: Schema


@dataclass
class LookupTable:
    """
    This table maps an integer key to a string value.

    :param id: Primary key.
    :param value: Lookup value.
    """

    id: PrimaryKey[int]
    value: str


@dataclass
class EntityTable:
    """
    This class represents a table in a database or data warehouse.

    :param primary_key: Primary key of the table.
    :param updated_at: The time the record was created or last modified.
    :param foreign_key: A column with a foreign key to another table.
    :param unique_key: A column with unique values only.
    """

    primary_key: PrimaryKey[int]
    updated_at: datetime
    foreign_key: LookupTable
    unique_key: Unique[str]


def send_message(
    sender: str,
    recipient: str,
    message_body: str,
    priority: int = 1,
) -> int:
    """
    :param sender: The person sending the message.
    :param recipient: The recipient of the message.
    :param message_body: The body of the message.
    :param priority: The priority of the message, can be a number 1-5.
    :returns: The message identifier.
    """
    pass