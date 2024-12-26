import sys

from end4train.app.monitor import Monitor


def main() -> None:
    monitor_app = Monitor(sys.argv)
    sys.exit(monitor_app.run())


if __name__ == "__main__":
    main()
