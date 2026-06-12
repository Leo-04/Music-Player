import os
import sys

from app import App
from modules.single import Single


def main():
    single = Single(Single.generate_port(
        __file__
        if os.path.exists(__file__)
        else sys.executable
    ))

    if single.is_not_main():
        return single.send_argv(sys.argv[1:])

    app = App(sys.argv[1:])

    single.callback = app.play_tracks_from_argv
    single.thread_loop()
    app.mainloop()

    single.close()
    os._exit(0)


if __name__ == "__main__":
    main()
