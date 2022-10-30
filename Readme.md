# Automatic Brightness Adjustment for Dell Displays

Tool to automatically adjust the brightness of dell displays which are compatible with the dell display manager

## Dependencies
Working Installation of the [dell display manager](https://www.google.com/search?q=dell+display+manager). Running on a windows OS, using the dell display manager API.

## Features
Define a characteristic curve over a whole day, this tool will automatically set the brightness to the selected values

## First Usage
1. Install Dell Display Manager
2. Install Python 3.9 Interpreter
3. Define a characteristic_curve:

![characteristic curve example](https://github.com/SvnGms/display-bightness-bot/blob/main/characteristic_curve_example.jpg?raw=true)

```
config.json = {
  "ddm_path": "C:\\Program Files (x86)\\Dell\\Dell Display Manager\\ddm.exe",
  "characteristic_line": [[0,1],[60, 1],[120, 1],[360, 10],[420, 13],[480, 16],[600, 85],[720, 100], [840, 100],[1020, 15],[1440, 5]]
}
```

edit the ```characteristic_line``` list of x,y datapoints to enable a different characteristic curve. Syntax of the datapoints: ```[<minute of day>,<display_brightness_percentage>]```

4. Start the app with a python interpreter: ```python main.py```

## Disclaimer
This is a side project for my own convenience, I was often changing display brightness during the day. Do not expect fixes regularly. If something breaks, please fix and create a pull request. Any contribution is appreciated.

## Collaboration
Any contribution is appreciated. Implement new Display Support, or improve characteristic curve generation
### Feature Ideas
1. Current Solution needs a fixed characteristic curve. Maybe there is a way to generate a curve, depending on the current locations sunrise and sunset?
2. Incorporate a light sensor, to set display brightness based on measurements?
3. Include similar display API's for different manufacturers
4. Setup as a windows service, to run in background?
5. Include different OS support?
