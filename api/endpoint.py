from dataclasses import dataclass, field
from enum import Enum
from typing import Union, Optional, Dict, List


class TypeEnum(Enum):
    STRING = 'string'
    INT = 'integer'
    BOOL = 'boolean'
    DATETIME = 'datetime'

    @classmethod
    def create(cls, value):
        if value == cls.STRING.value:
            return TypeEnum.STRING
        elif value == cls.INT.value:
            return TypeEnum.INT
        elif value == cls.BOOL.value:
            return TypeEnum.BOOL
        elif value == cls.DATETIME.value:
            return TypeEnum.DATETIME
        else:
            raise ValueError(f"Unknown TypeEnum value: {value}")


SchemaFieldType = Union['Object', 'Select', 'Field']


@dataclass
class Parameter:
    name: str
    type: TypeEnum
    operation: str
    condition: str
    required: bool
    description: str
    default: str
    example: str


@dataclass
class SQLParameter:
    name: str
    type: TypeEnum
    position: int
    description: str
    default: str
    example: str


@dataclass
class Object:
    name: Optional[str]
    description: str
    fields: Dict[str, SchemaFieldType]


@dataclass
class Select:
    endpoint: str
    params: Dict[str, str]
    description: str


@dataclass
class Field:
    type: TypeEnum
    db_name: str
    example: str
    description: str


def _collect_selects(field: SchemaFieldType):
    if isinstance(field, Select):
        return [field]
    elif isinstance(field, Object):
        return [
            select
            for child in field.fields.values()
            for select in _collect_selects(child)
        ]
    else:
        return []


@dataclass
class Endpoint:
    name: str
    sql: str
    schema: SchemaFieldType
    key: Optional[str]
    description: Optional[str]
    pagination_enabled: bool = False
    aggregation_enabled: bool = False

    params: List[Parameter] = field(default_factory=list)
    sql_params: List[SQLParameter] = field(default_factory=list)

    selects: List[Select] = field(init=False)

    def __post_init__(self):
        self.selects = _collect_selects(self.schema)
