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


# TODO: receiver -> countdown_receiver
# or change the constructor
@dataclass
class Timer:
    receiver: ""
    is_terminated: bool = False

    @property
    def time_remaining_sec(self):
        return 0 if self.is_terminated else self.receiver.value

    def run(self):
        receiver_disposable = self.receiver.subscribe()

        def terminate():
            receiver_disposable.dispose()
            self.is_terminated = True

        return Disposable(terminate)


def create_timer(
    time_sec_init,
    countdown_obs=None,
    subscribe_on=None,
    observe_on=None,
):
    if countdown_obs is None:
        countdown_obs = create_countdown_obs(time_sec_init)

    return Timer(
        Receiver(
            countdown_obs,
            value=time_sec_init,
            subscribe_on=None,
            observe_on=None,
        )
    )
