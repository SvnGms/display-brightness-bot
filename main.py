import click
import time
import json
from pathlib import Path
import subprocess
from scipy.interpolate import interp1d
from scipy import interpolate
import matplotlib.pyplot as plt
import numpy as np

"""
    Config Syntax:
        characteristic line is a list of tuples. A tuple represents (<minute of day>,<brightness percentage>)
"""
default_json = {
    "ddm_path": "C:\\Program Files (x86)\\Dell\\Dell Display Manager\\ddm.exe",
    "characteristic_line": [[1440, 5], [840, 100]],
}


def validate_config(config):
    """
        Validaates the config

        ToDo: validate the characteristic curve
    :param config: configuration dictionary to validate
    :return: throws exception in case of misconfiguration
    """
    ddm = Path(config["ddm_path"])
    if not ddm.exists():
        raise ValueError("ddm.exe could not be found")
    # config["characteristic_line"]


def interpolate_characteristic_line(config, showgraph):
    """
        Interpolates the datapoints of the brightness characteristic line

        ToDo: Use periodic interpolation to eliminate the gap at 24h
    """
    minutes_of_day = 24 * 60
    l = config["characteristic_line"]
    l.sort(key=lambda x: x[0])
    result = list(map(list, zip(*l)))
    x, y = result

    f = interp1d(x, y)
    f2 = interp1d(x, y, kind='cubic')

    tck = interpolate.splrep(x, y, s=0)
    xnew2 = np.arange(0, minutes_of_day, 60)
    ynew2 = interpolate.splev(xnew2, tck, der=0)

    xnew = np.linspace(min(x), max(x), num=minutes_of_day, endpoint=True)

    if showgraph:
        plt.plot(x, y, 'o', xnew, f(xnew), '-', xnew, f2(xnew), '--', xnew2, ynew2, ':')
        plt.legend(['data', 'linear', 'cubic', 'spline'], loc='best')
        plt.show()

    # use linear interpolation for now, as it provides the minimal gap between 24:00 and 0:00, if configured okay
    return xnew, f(xnew)


def set_brightness(config, brightness_percentage):
    process = subprocess.run([config["ddm_path"], '/SetBrightnessLevel', str(brightness_percentage)],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True, check=True)


@click.command()
@click.option('--interval', default=1, help='update interval in minutes')
@click.option('--showgraph', default=True, help='start with interpolation graph')
def main(interval, showgraph):
    click.echo('Hello World!')

    try:
        conf_file = Path("./config.json")
        with open(conf_file) as f:
            config = json.load(f)
        validate_config(config)
    except Exception as e:
        print(e)
        config = default_json
    print("Using config:", config)

    x, f_x = interpolate_characteristic_line(config, showgraph)
    # run brightness scheduler here
    while True:
        now = time.localtime()
        minute_of_day = now.tm_hour * 60 + now.tm_min
        set_brightness(config, f_x[minute_of_day])
        print(time.strftime("%x  %H:%M:%S", now), "Brightness set to: ", f_x[minute_of_day])
        time.sleep(interval * 60)


if __name__ == '__main__':
    main()
