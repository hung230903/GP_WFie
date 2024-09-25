import pywifi
from pywifi import const
import time

# Function to scan for available Wi-Fi networks
def scan_wifi():
    wifi = pywifi.PyWiFi()  # Initialize the PyWiFi object
    iface = wifi.interfaces()[0]  # Get the first wireless interface
    iface.scan()  # Start scanning for Wi-Fi networks
    time.sleep(3)  # Wait for scan results

    networks = iface.scan_results()  # Get scan results

    # Print list of available networks with SSID and index
    print(f"\n{'Index':<5}{'SSID':<30}{'Signal (dBm)':<15}")
    print("=" * 50)
    for idx, network in enumerate(networks):
        ssid = network.ssid
        signal = network.signal
        print(f"{idx:<5}{ssid:<30}{signal:<15}")

    return networks  # Return the scanned networks

# Function to select up to 4 networks to focus on
def choose_routers(networks):
    selected_routers = []
    
    while len(selected_routers) < 4:
        try:
            index = int(input(f"\nEnter the index of the router to focus on (selected {len(selected_routers)}/4): "))
            if 0 <= index < len(networks):
                selected_routers.append(networks[index])
            else:
                print("Invalid index. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    return selected_routers  # Return the selected routers

# Function to monitor selected routers' signal strength
def monitor_selected_routers(routers):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]

    try:
        while True:
            iface.scan()  # Continuously scan for updated signal strengths
            time.sleep(3)  # Sleep for 3 seconds to let the scan complete
            networks = iface.scan_results()

            # Find the updated signal strength for the selected routers
            print(f"\n{'SSID':<30}{'Signal (dBm)':<15}")
            print("=" * 45)
            for router in routers:
                for network in networks:
                    if network.ssid == router.ssid:
                        print(f"{network.ssid:<30}{network.signal:<15}")
                        break
            print("\nPress Ctrl+C to stop monitoring.")
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    # Step 1: Scan available networks
    available_networks = scan_wifi()

    # Step 2: Choose up to 4 routers to focus on
    focused_routers = choose_routers(available_networks)

    # Step 3: Continuously monitor the signal strength of the selected routers
    monitor_selected_routers(focused_routers)
