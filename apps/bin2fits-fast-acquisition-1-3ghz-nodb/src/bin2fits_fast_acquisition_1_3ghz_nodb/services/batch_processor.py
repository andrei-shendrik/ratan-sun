import time
import psutil
import signal
import logging
import concurrent.futures
from pathlib import Path
from typing import List

from bin2fits_fast_acquisition_1_3ghz_nodb.services.task_report import TaskReport
from bin2fits_fast_acquisition_1_3ghz_nodb.services.parallel_worker import execute_worker_task, ParallelWorker
from bin2fits_fast_acquisition_1_3ghz_nodb.settings.bin2fits_fast_acquisition_1_3ghz_settings import \
    Bin2FitsFastAcquisition1To3GHzSettings
from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.domain import ProcessingResult
from ratanpy.utils.process_profiler import ProcessProfiler


class BatchProcessor:
    def __init__(self, settings: Bin2FitsFastAcquisition1To3GHzSettings):
        self._settings = settings
        self._logger = logging.getLogger("batch_processor")
        self._shutdown_requested = False

        # перехват ctrl+c для Graceful Shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        self._logger.warning("\nStop requested by user (Ctrl+C). Waiting for the current tasks to be completed...")
        self._shutdown_requested = True

    def _wait_for_ram(self):
        """ Ожидание ОЗУ СНАРУЖИ пула процессов """
        min_ram_gb = self._settings.resources.min_free_ram_gb
        while True:
            if self._shutdown_requested:
                return False
            available_gb = psutil.virtual_memory().available / (1024 ** 3)
            if available_gb >= min_ram_gb:
                return True
            self._logger.warning(f"System RAM low ({available_gb:.1f}GB < {min_ram_gb}GB). Waiting...")
            time.sleep(5)

    def run(self, files: List[Path], fits_dir: Path, workers: int, overwrite: bool, report: TaskReport) -> TaskReport:
        total = len(files)

        with ProcessProfiler() as batch_profiler:
            with concurrent.futures.ProcessPoolExecutor(
                    max_workers=workers,
                    initializer=ParallelWorker.init_pool,
                    initargs=(self._settings.resources.worker_max_ram_gb,)
            ) as executor:

                future_to_file = {}
                file_iterator = iter(enumerate(files, 1))

                def submit_next():
                    if self._shutdown_requested or not self._wait_for_ram():
                        return
                    try:
                        idx, f = next(file_iterator)
                        # передача задачи в дочерний процесс
                        new_future = executor.submit(
                            execute_worker_task, f, fits_dir, overwrite, idx, total, self._settings
                        )
                        future_to_file[new_future] = f
                    except StopIteration:
                        pass

                # первичное заполнение очереди (2x от числа воркеров, чтобы пул не простаивал)
                for _ in range(workers * 2):
                    submit_next()

                # сбор результатов по мере готовности
                while future_to_file:
                    done, _ = concurrent.futures.wait(
                        future_to_file.keys(),
                        return_when=concurrent.futures.FIRST_COMPLETED
                    )

                    for future in done:
                        original_file = future_to_file.pop(future)
                        try:
                            res: ProcessingResult = future.result()

                            # вывод изолированных логов из воркера в главный поток
                            for record in res.log_records:
                                logging.getLogger().handle(record)

                            # обновление статистики отчета
                            report.update(res)

                        except Exception as e:
                            self._logger.critical(f"Process crashed for {original_file.name}: {e}")
                            report.failed += 1

                        # задача завершилась, закидывается следующая
                        submit_next()

        report.total_time_sec = batch_profiler.elapsed_seconds
        report.formatted_time = batch_profiler.formatted_time

        return report