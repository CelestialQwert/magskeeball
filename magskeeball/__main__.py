import argparse
import sys

choices = ['game', 'sensor_test']

parser = argparse.ArgumentParser()
parser.add_argument(
    'test_mode', choices=choices, default='game', const='game', nargs='?'
)
test_mode = parser.parse_args().test_mode

if test_mode == 'sensor_test':
    from .import sensor
    sensor.main()
else:
    from . import main
    main.run()
