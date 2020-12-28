import multiprocessing
from dataclasses import dataclass

from rx.scheduler import ThreadPoolScheduler
import rx.operators as op

rx_background_scheduler = ThreadPoolScheduler(max_workers=multiprocessing.cpu_count())


@dataclass
class Receiver:
    """Stores and updates the most recent value emitted by an observable."""
    obs: ""
    value: "" = None

    def subscribe(self):

        def set_value(value):
            self.value = value

        return self.obs.subscribe(set_value)
