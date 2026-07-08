from enum import Enum


class AdvancedEnum(Enum):
    """
    Расширенный Enum класс:
    нечувствительный к регистру парсинг из строк
    """
    @classmethod
    def from_string(cls, val: str) -> 'AdvancedEnum':
        if not val:
            raise ValueError(f"Value for {cls.__name__} is missing or empty")

        # удаление пробелов и приведение к нижнему регистру
        clean_val = str(val).strip().lower()

        # поиск по .value
        for member in cls:
            if str(member.value).lower() == clean_val:
                return member

        # поиск по .key
        # замена дефисов и пробелов на подчеркивания
        clean_key = clean_val.replace(' ', '_').replace('-', '_')
        for member in cls:
            if member.name.lower() == clean_key:
                return member

        raise ValueError(f"'{val}' is not a valid value for {cls.__name__}")