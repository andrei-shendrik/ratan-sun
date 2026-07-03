import threading
import time
import psutil


class ProcessProfiler:
    """
    Контекстный менеджер для замера времени выполнения и
    пикового потребления памяти (RAM) текущим процессом.
    """

    def __init__(self):
        self.start_time = 0.0
        self.elapsed_seconds = 0.0
        self.peak_memory_mb = 0.0
        self._process = psutil.Process()
        self._stop_event = threading.Event()
        self._monitor_thread = None

    def _monitor_ram(self):
        """ замеряет память каждые 0.1 секунды """
        while not self._stop_event.is_set():
            current_mb = self._process.memory_info().rss / (1024 * 1024)
            if current_mb > self.peak_memory_mb:
                self.peak_memory_mb = current_mb
            time.sleep(0.1)

    def __enter__(self):
        self.start_time = time.perf_counter()

        # фиксация базовой памяти при старте задачи
        self.peak_memory_mb = self._process.memory_info().rss / (1024 * 1024)
        self._stop_event.clear()

        # запуск наблюдателя (daemon=True)
        self._monitor_thread = threading.Thread(target=self._monitor_ram, daemon=True)
        self._monitor_thread.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # остановка наблюдателя
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)

        self.elapsed_seconds = time.perf_counter() - self.start_time

    @property
    def formatted_time(self) -> str:
        m, s = divmod(int(self.elapsed_seconds), 60)
        h, m = divmod(m, 60)
        return f"{h}h {m}m {s}s" if h > 0 else f"{m}m {s}s"

# class ProcessProfiler:
#     """
#     Контекстный менеджер для замера времени выполнения
#     и пикового потребления памяти (RAM) текущим процессом.
#     """
#     def __init__(self):
#         self.start_time = 0.0
#         self.end_time = 0.0
#         self.elapsed_seconds = 0.0
#         self.peak_memory_mb = 0.0
#         # Запоминаем текущий процесс
#         self._process = psutil.Process()
#
#     def __enter__(self):
#         self.start_time = time.perf_counter()
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.end_time = time.perf_counter()
#         self.elapsed_seconds = self.end_time - self.start_time
#
#         # Получаем пиковое потребление памяти
#         if sys.platform != 'win32':
#             # На Linux/UNIX встроенный модуль resource делает это идеально (возвращает в Килобайтах)
#             import resource
#             usage = resource.getrusage(resource.RUSAGE_SELF)
#             self.peak_memory_mb = usage.ru_maxrss / 1024.0
#         else:
#             # На Windows ru_maxrss не работает. Используем psutil для получения пика памяти (Peak Working Set)
#             memory_info = self._process.memory_info()
#             # В Windows атрибут peak_wset хранит пиковое значение в байтах
#             if hasattr(memory_info, 'peak_wset'):
#                 self.peak_memory_mb = memory_info.peak_wset / (1024 * 1024)
#             else:
#                 # Fallback, если атрибута нет (просто текущая память)
#                 self.peak_memory_mb = memory_info.rss / (1024 * 1024)
#
#     @property
#     def formatted_time(self) -> str:
#         """Возвращает время в формате ЧЧ:ММ:СС"""
#         m, s = divmod(int(self.elapsed_seconds), 60)
#         h, m = divmod(m, 60)
#         if h > 0:
#             return f"{h}h {m}m {s}s"
#         return f"{m}m {s}s"