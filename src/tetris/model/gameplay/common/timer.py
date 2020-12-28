from dataclasses import dataclass

import rx
from rx import operators as op
from rx.disposable import Disposable

from common.util.concurrency import Receiver


def create_countdown_obs(countown_sec, scheduler=None):
    """Create an observable sequence descending from the given number to zero, inclusive.
    
    Emits one value per second, starting immediately."""
    return rx.concat(
        rx.of(countown_sec), 
        rx.interval(1, scheduler=scheduler).pipe(
            op.take(countown_sec), 
            op.map(lambda v: countown_sec - 1 - v),
        ),
    )


@dataclass
class Timer:
    countdown_receiver: ""
    is_terminated: bool = False

    @property
    def time_remaining_sec(self):
        return 0 if self.is_terminated else self.countdown_receiver.value

    def run(self):
        countdown_receiver_disposable = self.countdown_receiver.subscribe()

        def terminate():
            countdown_receiver_disposable.dispose()
            self.is_terminated = True

        return Disposable(terminate)


def create_timer(countdown_obs, time_sec_init):
    return Timer(Receiver(countdown_obs, value=time_sec_init))
