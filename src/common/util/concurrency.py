import multiprocessing

from rx.scheduler import ThreadPoolScheduler

rx_background_scheduler = ThreadPoolScheduler(multiprocessing.cpu_count())