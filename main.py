import click
import time
import json
from pathlib import Path
import subprocess
from scipy.interpolate import interp1d
from scipy import interpolate
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread
import geocoder
from astral.sun import sun
from astral import LocationInfo
import datetime
from timezonefinder import TimezoneFinder

"""
    Config Syntax:
        characteristic line is a list of tuples. A tuple represents (<minute of day>,<brightness percentage>)
"""
default_json = {
    "ddm_path": "C:\\Program Files (x86)\\Dell\\Dell Display Manager\\ddm.exe",
    "characteristic_line": [[0, 1], [60, 1], [120, 1], [360, 10], [420, 13], [480, 16], [600, 85], [720, 100],
                            [840, 100], [1020, 15], [1440, 5]],
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
    x_spline = np.arange(0, minutes_of_day, 60)
    y_spline = interpolate.splev(x_spline, tck, der=0)

    x_samples = np.linspace(min(x), max(x), num=minutes_of_day, endpoint=True)

    if showgraph:
        x_ = [e / 60 for e in x]
        x_samples_ = [e / 60 for e in x_samples]
        x_spline = [e / 60 for e in x_spline]
        plt.plot(x_, y, 'o', x_samples_, f(x_samples), '-', x_samples_, f2(x_samples), '--', x_spline, y_spline, ':')
        plt.legend(['data', 'linear', 'cubic', 'spline'], loc='best')
        plt.xlabel('hour')
        plt.ylabel('brightness percentage')
        plt.show()

    # use linear interpolation for now, as it provides the minimal gap between 24:00 and 0:00, if configured okay
    return x_samples, f(x_samples)


def set_brightness(config, brightness_percentage):
    process = subprocess.run([config["ddm_path"], '/SetBrightnessLevel', str(brightness_percentage)],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True, check=True)


def wait_for_next_interpolation_step(interval):
    """

    :param interval: time interval in minutes
    :return:
    """
    time.sleep(interval * 60)


def min_of_day(datetime: datetime):
    return int(datetime.hour*60 + datetime.minute)

def generate_characteristic_curve_based_on_sunset_sunrise():
    g = geocoder.ip('me')
    print(g.latlng)

    tf = TimezoneFinder()
    time_zone = tf.timezone_at(lat=g.lat, lng=g.lng)

    city = LocationInfo(g.city, g.state, str(time_zone), 51.5, -0.116)
    sun_info = sun(city.observer, date=datetime.datetime.today())

    characteristic_line = [[min_of_day(sun_info["dawn"]), 5], [min_of_day(sun_info["sunrise"]), 25], [min_of_day(sun_info["sunrise"])+120, 100], [min_of_day(sun_info["noon"]), 100], [min_of_day(sun_info["sunset"])-120, 100], [min_of_day(sun_info["sunset"]), 25], [min_of_day(sun_info["dusk"]), 5]]
    return characteristic_line


@click.command()
@click.option('--interval', default=1, help='update interval in minutes')
@click.option('--showgraph', default=False, help='start with interpolation graph')
@click.option('--chracteristic_line', default='sunset', help='characteristic curve to use: "config" for  custom config, "sunset" for calculation based on sunset/sunrise')
def main(interval, showgraph, chracteristic_line):
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

    if chracteristic_line == "sunset":
        c_line = generate_characteristic_curve_based_on_sunset_sunrise()
        config['characteristic_line']
    x, f_x = interpolate_characteristic_line(config, showgraph)



    # run brightness scheduler here
    while True:
        now = time.localtime()
        minute_of_day = now.tm_hour * 60 + now.tm_min
        set_brightness(config, int(f_x[minute_of_day]))
        print(time.strftime("%x  %H:%M:%S", now), "Brightness set to: ", int(f_x[minute_of_day]), '%')
        thread = Thread(target=wait_for_next_interpolation_step, args=(interval,))
        thread.start()
        thread.join()


if __name__ == '__main__':
    main()
