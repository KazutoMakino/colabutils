"""Keep on running colab runtime.

Usage:
- `py running.py -u {active google colab's url}`
- `py running.py -u {active google colab's url} -s True`

---

KazutoMakino

"""

import os
import random
import sys
import time
import traceback
import webbrowser
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint

import pyautogui as pg
import pytz

#######################################################################################
# main
#######################################################################################


def main():
    AutoColabRunner.run()


#######################################################################################
# class
#######################################################################################


class AutoColabRunner:
    @staticmethod
    def run() -> None:
        # get args
        args = ArgsGetter.get_args()

        # reload web page
        WebBrowser.is_reloaded(
            app_name=args.app,
            cycles=args.cycles,
            sleep_time=args.time,
            url=args.url,
            gui_auto=args.gui,
            check_time_interval=args.interval,
            is_shutdown=args.shutdown,
        )

        # show message box
        pg.alert(text="complete", title="end", timeout=60 * 60)


class ArgsGetter:
    @staticmethod
    def get_args() -> ArgumentParser.parse_args:
        """Get command line arguments.

        Returns:
            ArgumentParser.parse_args: Command line arguments.
        """
        # get parameters from command line
        parser = ArgumentParser(description="Recursively reloading the web page.")
        parser.add_argument(
            "-a",
            "--app",
            type=str,
            default="chrome",
            help="application name (chrome, edge, firefox, safari)",
        )
        parser.add_argument(
            "-c",
            "--cycles",
            type=int,
            default=12 * 2,
            help="number of recursion",
        )
        parser.add_argument(
            "-t",
            "--time",
            type=float,
            default=60 * 30,
            help="sleep time [s] per cycle",
        )
        parser.add_argument(
            "-u",
            "--url",
            type=str,
            default="https://www.google.co.jp/",
            help="URL of web page",
        )
        parser.add_argument(
            "-g",
            "--gui",
            type=bool,
            default=True,
            help="GUI Automation",
        )
        parser.add_argument(
            "-i",
            "--interval",
            type=float,
            default=5,
            help="time interval of GUI Automation",
        )
        parser.add_argument(
            "-s",
            "--shutdown",
            type=bool,
            default=False,
            help="shutdown or not of the end",
        )

        # get args
        args = parser.parse_args()
        return args


class WebBrowser:
    # get application path (windows: nt, mac/linux: posix)
    app_path = {
        "nt": {
            "chrome": "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            "edge": "",
            "firefox": "",
            "safari": "",
        },
        "posix": {
            "chrome": "",
            "edge": "",
            "firefox": "",
            "safari": "",
        },
    }

    @classmethod
    def is_reloaded(
        cls,
        app_name: str = "chrome",
        cycles: int = 12,
        sleep_time: float = 1,
        url: str = "https://www.google.co.jp/",
        gui_auto: bool = True,
        check_time_interval: float = 5,
        is_shutdown: bool = False,
    ) -> None:
        # show parameters
        pprint(
            {
                "app_name": app_name,
                "cycles": cycles,
                "sleep_time": sleep_time,
                "gui_auto": gui_auto,
                "url": url,
                "check_time_interval": check_time_interval,
                "is_shutdown": is_shutdown,
            }
        )

        # recursive reload web page per sleep_time
        time_now = datetime.now(tz=pytz.timezone("Asia/Tokyo"))
        deadline = time_now + timedelta(seconds=cycles * sleep_time)
        print(f"now: {time_now}")
        print(f"-> end this routine: {deadline}")
        print("--------------------------------------------------")
        for i in range(cycles):
            # get web browser application
            browser_app = cls.app_path[os.name][app_name]
            browse = webbrowser.get(f"{browser_app} %s")

            # reload url
            browse.open(url=url)
            print(
                f"iteration: {i+1}/{cycles}, "
                + f'now: {datetime.now(tz=pytz.timezone("Asia/Tokyo"))}'
            )

            if gui_auto:
                # init
                elapsed_time = 0

                # loop: elapsed_time < sleep_time
                while elapsed_time < sleep_time:
                    # get start time
                    start_time = time.perf_counter()

                    # take a nup
                    time.sleep(check_time_interval)

                    # set image path
                    img_path = (
                        Path(__file__).parent.resolve() / "img/are_you_a_robot.jpg"
                    )

                    # check and GUI operation
                    xy = GUIHandler.get_matched_figure_area(
                        img_path=img_path, try_count=1
                    )
                    if xy:
                        time.sleep(random.random())
                        pg.moveTo(
                            x=xy["left"] + 152,
                            y=xy["top"] + 174,
                            duration=3 * random.random(),
                        )
                        time.sleep(random.random())
                        pg.leftClick()
                        time.sleep(random.random())

                    # add elapsed time to elapsed_time
                    elapsed_time += time.perf_counter() - start_time

            else:
                # sleep
                time.sleep(sleep_time)

        # shutdown
        if is_shutdown:
            print("This system will be shutdown after 60 [s]")
            time.sleep(60)
            os.system("shutdown -s")


class GUIHandler:
    """Handlers of GUI operation."""

    @staticmethod
    def gui_fail_safe(pause_time: float = 1, failsafe: bool = True) -> None:
        """Fail-safe settings of auto GUI operation.

        Args:
            pause_time (float, optional):
                A pause time interval @ pyautogui's mouse/key operations.
                Defaults to 1.
            failsafe (bool, optional):
                A definition of pyautogui fail safe mode setting.
                Defaults to True.
        """
        # set fail safe
        pg.FAILSAFE = failsafe
        # set pause time @ moving the mouse
        if failsafe:
            pg.PAUSE = pause_time

    @staticmethod
    def get_matched_figure_area(
        img_path: Path,
        confidence: float = 0.8,
        ret: bool = True,
        try_count: int = 10,
        interval: float = 1,
    ) -> dict:
        """Get the matched figure area.

        Args:
            img_path (Path): A file path.
            confidence (float, optional):
                A degree of confidence of image recognition.
                Defaults to 0.9.
            ret (bool, optional): Return or not. Defaults to True.
            try_count (int, optional): Counter of trying this task.
                Defaults to 10.
            interval (float, optional): Waiting time of each trial.
                Defaults to 1.

        Returns:
            dict: The matched area parameters at dict type.
        """
        # loop: get figure position
        # print("Searching:", img_path)
        for i in range(try_count):
            # print("    count: {0} / {1}".format(i, try_count))
            try:
                # get figure position
                screen_fig = pg.locateOnScreen(str(img_path), confidence=confidence)
                if screen_fig:
                    break
            except pg.ImageNotFoundException:
                time.sleep(interval)
        if screen_fig is None:
            # AttributeError(f"not found: {img_path.resolve()}")
            # sys.exit()
            return None
        elif not ret:
            return
        # get position / size
        left, top, right, bottom = screen_fig
        width, height = right - left, bottom - top
        center_x, center_y = int(round(right - left)), int(round(bottom - top))
        if ret:
            return {
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom,
                "width": width,
                "height": height,
                "center_x": center_x,
                "center_y": center_y,
            }


#######################################################################################

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
    sys.exit()
