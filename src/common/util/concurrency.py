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
    subscribe_on: "" = None
    observe_on: "" = None

    def subscribe(self):

        def set_value(value):
            self.value = value
        
        ops = []

        if self.subscribe_on is not None:
            ops.append(op.subscribe_on(self.subscribe_on))
        if self.observe_on is not None:
            ops.append(op.observe_on(self.observe_on))

        return self.obs.pipe(*ops).subscribe(set_value)