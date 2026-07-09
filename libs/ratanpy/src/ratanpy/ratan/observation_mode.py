from ratanpy.common.advanced_enum import AdvancedEnum


class ObservationMode(AdvancedEnum):
    """
    Режимы наблюдений

    Regular = обычное наблюдение
    Tracking = режим сопровождения активной области (диаграмма удерживается на определенной координате Солнца)
    Scanning = режим сканирования Солнца (кареткой сканируется Солнце)
    """
    REGULAR = "Regular"
    TRACKING = "Tracking"
    SCANNING = "Scanning"