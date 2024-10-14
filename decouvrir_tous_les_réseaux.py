import subprocess
import time
import re
import platform
import matplotlib.pyplot as plot
import numpy as np

def read_from_cmd():
    if platform.system() == 'Linux':
        process = subprocess.Popen("nmcli dev wifi list", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif platform.system() == 'Windows':
        process = subprocess.Popen("netsh wlan show networks mode=bssid", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        raise Exception('Unsupported OS')

    output, error = process.communicate()
    output = output.decode('latin-1')
    return output

def parse_output(output):
    if platform.system() == 'Linux':
        networks = output.splitlines()[1:]  # Ignore header
        strongest_signal = -100  # Very low signal
        strongest_ssid = None

        for line in networks:
            if line.strip():  # Ignore empty lines
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) > 5:  # Ensure there are enough parts
                    ssid = parts[0]
                    signal = int(parts[5])  # Signal strength is in the 6th column

                    if signal > strongest_signal:
                        strongest_signal = signal
                        strongest_ssid = ssid

        return strongest_ssid, strongest_signal
    elif platform.system() == 'Windows':
        networks = []
        for line in output.splitlines():
            if 'SSID' in line:
                ssid = line.split(':')[1].strip()
                signal_line = next((l for l in output.splitlines() if 'Signal' in l and ssid in l), None)
                if signal_line:
                    signal_match = re.search(r'(\d+)%', signal_line)
                    if signal_match:
                        signal = int(signal_match.group(1))
                    else:
                        signal = 0  # default signal strength if not found
                else:
                    signal = 0  # default signal strength if not found
                networks.append((ssid, signal))

        strongest_ssid = max(networks, key=lambda x: x[1])[0]
        strongest_signal = max(networks, key=lambda x: x[1])[1]

        return strongest_ssid, strongest_signal
    else:
        raise Exception('Unsupported OS')

def connect_to_strongest_wifi(ssid, signal):
    if platform.system() == 'Linux':
        subprocess.run(["nmcli", "dev", "wifi", "connect", ssid])
    elif platform.system() == 'Windows':
        subprocess.run(["netsh", "wlan", "connect", ssid])
    else:
        raise Exception('Unsupported OS')

def display_wifi_info():
    while True:
        output = read_from_cmd()
        ssid, signal = parse_output(output)
        print(f"Strongest WiFi: {ssid} with signal strength {signal}dBm")
        connect_to_strongest_wifi(ssid, signal)
        time.sleep(5)

if __name__ == "__main__":
    display_wifi_info()