from enum import Enum

from sqlalchemy import MetaData
from sqlmodel import SQLModel

CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class BaseModel(SQLModel):
    metadata = MetaData(naming_convention=CONVENTION)


def enum_values(enum_cls: type[Enum]) -> list[str]:
    return [item.value for item in enum_cls]
