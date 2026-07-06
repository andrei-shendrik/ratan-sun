# переопределение отображения даты и времени для английской локали
# влияет на Django Admin, Django Templates, Django Forms
DATETIME_FORMAT = 'd M Y, H:i:s'         # 06 Jul 2026, 14:30:00
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'      # 06/07/2026 14:30
TIME_FORMAT = 'H:i:s'                    # 14:30:00