import logging
from enum import Enum
from typing import TypeVar, Type

from django.db import models

logger = logging.getLogger(__name__)

T_Enum = TypeVar('T_Enum', bound=Enum)
T_DjangoChoices = TypeVar('T_DjangoChoices', bound=models.TextChoices)


class EnumMapper:
    """ Утилита для трансляции Enum в константы БД Django """

    @staticmethod
    def map_enum_to_db_choices(domain_enum: T_Enum | None,
                               django_choices: Type[T_DjangoChoices]) -> str | None:
        if not domain_enum:
            return None

        django_enum_member = django_choices.__members__.get(domain_enum.name)

        if isinstance(django_enum_member, Enum):
            return str(django_enum_member.value)

        logger.warning(
            f"Enum mapping failed: '{domain_enum.name}' not found "
            f"in {django_choices.__name__}"
        )
        return None