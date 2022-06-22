"""Timer of Google Colaboratory.

Usage:
- `deadline = ColabTimer.get_deadline()`

---

KazutoMakino

"""

import subprocess
from datetime import datetime, timedelta

import pytz

#######################################################################################
# class
#######################################################################################


class ColabTimer:
    """Timer of Google Colaboratory."""

    @staticmethod
    def get_elapsed_time() -> float:
        """Get elapsed time of this session.

        Returns:
            float: Elapsed time of this session.
        """
        # !cat /proc/uptime | awk '{printf("%f", $1)}'
        ret = subprocess.run(
            ["cat", "/proc/uptime", "|", "awk", '{printf("elapsed[s]: %f", $1)}'],
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        return float(ret.stdout.split(" ")[0])

    @staticmethod
    def get_deadline(
        session_time: float = 12 * 60 * 60,
        margin: float = 10 * 60,
        time_zone: str = "Asia/Tokyo",
        is_show: bool = True,
    ) -> datetime:
        """Get the deadline datetime.

        Args:
            session_time (float, optional): Max session time [s] @ colab.
                Defaults to 12*60*60.
            margin (float, optional): Margin time [s] of the deadline.
                Defaults to 10*60.
            time_zone (str, optional): Time zone name.
                Defaults to "Asia/Tokyo".
            is_show (bool, optional): Show or not.
                Defaults to True.

        Raises:
            ValueError: The elapsed time is larger than the session time.

        Returns:
            datetime: the deadline datetime of this session.
        """
        # get elapsed time
        elapsed_time = ColabTimer.get_elapsed_time()

        if elapsed_time >= session_time:
            raise ValueError(
                "What's happened !? The elapsed time is larger than the session time"
                + f" ({elapsed_time} >= {session_time})."
            )

        # get remaining time [s]
        remaining_time = session_time - elapsed_time - margin

        # get deadline datetime
        deadline = datetime.now(tz=pytz.timezone(zone=time_zone)) + timedelta(
            seconds=remaining_time
        )

        # show
        if is_show:
            print(f"deadline: {deadline}, margin={margin} [s]")

        return deadline
