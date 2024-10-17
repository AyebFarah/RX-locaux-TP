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
        raise Exception('Unspoorted OS')

    output, error = process.communicate()
    output = output.decode('latin-1')
    return output


def parse_output(output):
    if platform.system() == 'Linux':
        networks = output.splitlines()[1:]
        strongest_signal = -100
        strongest_ssid = None

        for line in networks:
            if line.strip():
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) > 5:
                    ssid = parts[0]
                    signal = int(parts[5])

                    if signal > strongest_signal:
                        strongest_signal = signal
                        strongest_ssid = ssid

        return strongest_ssid, strongest_signal
    
    
    elif platform.system() == 'Windows':
        signals = re.findall(r'Signal\s*:\s*(\d+)%', output)
        
        ssids = []
        for line in output.splitlines():
            if 'SSID' in line:
                cleaned_line = re.sub(r'[^\x20-\x7E]', '', line).strip()
                if cleaned_line.startswith('SSID'):
                    ssid = cleaned_line.split(':')[1].strip()
                    ssids.append(ssid)
                    
        # ssids = re.findall(r'SSID\s\d+\s:\s([^\r\n]+)', out, re.DOTALL) 

        networks = list(zip(ssids, signals))
        return networks

    else:
        raise Exception('Unsupported OS')



def connect_to_strongest_wifi(ssid, signal):
    if platform.system() == 'Linux':
        command = ["nmcli", "dev", "wifi", "connect", ssid]
    elif platform.system() == 'Windows':
        command = ["netsh", "wlan", "connect", ssid]
    else:
        raise Exception('Unsupported OS')

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    if process.returncode == 0:
        print(f"Connecté à : {ssid}")
    else:
        print(f"Erreur de connection à {ssid}. Erreur rencontrée: {error.decode('latin-1')}")



def display_wifi_info():
    while True:
        output = read_from_cmd()
        networks = parse_output(output)
        
        print('\n***********************\n')
            
        if len(networks) == 0 :
            print("Pas de points d\'accès.")
            return;
        
        print('Points \'accès disponibles :')
        for i, network in enumerate(networks):
            print(f"{i + 1}. SSID: {network[0]}, Signal: {network[1]}%")
            
        print('')
        
        
        strongest_network = max(networks, key=lambda x: int(x[1]))
        ssid, signal = strongest_network
        
        print(f"SSID du meilleur point d\'accès: {ssid}")
        print(f"Signal du meilleur point d\'accès: {signal}%")
        connect_to_strongest_wifi(ssid, signal)
        
        
        time.sleep(5)


if __name__ == "__main__":
    display_wifi_info()

    
    