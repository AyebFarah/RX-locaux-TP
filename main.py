import subprocess
import re
import platform
import matplotlib.pyplot as plot
import numpy as np

def get_signal_strength():
    if platform.system() == 'Linux':
        process = subprocess.Popen("iwconfig", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif platform.system() == 'Windows':
        process = subprocess.Popen("netsh wlan show interfaces", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        raise Exception('Unsupported OS')

    output = process.stdout.read().decode('latin-1')

    if platform.system() == 'Linux':
        matches = re.findall('(wlan[0-9]+).*?Signal level=(-[0-9]+) dBm', output, re.DOTALL)
        return int(matches[0][1]) if matches else None
    elif platform.system() == 'Windows':
        matches = re.findall('Signal.*?:.*?([0-9]*)%', output, re.DOTALL)
        return (int(matches[0]) / 100 * 100) if matches else None
    else:
        raise Exception('Unsupported OS')

signal_strength_values = []

figure, axe = plot.subplots()
line_plot, = axe.plot([], [], lw=2)
axe.set_xlim(0, 100)
axe.set_ylim(0, 100)
axe.set_xlabel('Time (s)')
axe.set_ylabel('Signal Strength (dBm)')
axe.set_title('Signal Strength Monitoring of Access Point')

try:
    while True:
        signal_strength = get_signal_strength()

        if signal_strength is not None:
            signal_strength_values.append(signal_strength)

            if len(signal_strength_values) > 100:
                signal_strength_values.pop(0)

            line_plot.set_data(np.arange(len(signal_strength_values)), signal_strength_values)

            axe.draw_artist(line_plot)
            plot.pause(1)

        plot.draw()

except KeyboardInterrupt:
    print("Arrêté par l'utilisateur")