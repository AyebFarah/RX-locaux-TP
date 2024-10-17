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
        if matches:
            percent = int(matches[0])
            return percent_to_dBm(percent)
        return None
    else:
        raise Exception('Unsupported OS')

def percent_to_dBm(percent):
    PdBm_max = 0 
    PdBm_min = -100
    dBm = PdBm_max - ((PdBm_max - PdBm_min) * (100 - percent) / 100)

    return dBm

signal_strength_values = []

figure, axe = plot.subplots()
line_plot, = axe.plot([], [], lw=2)
axe.set_xlim(0, 100)
axe.set_ylim(-100, 0)
axe.set_xlabel('Temps (s)')
axe.set_ylabel('Puissance du signal (dBm)')
axe.set_title("Puissance du signal d'un point d'accès")

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
