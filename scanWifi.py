import pywifi
import time
import numpy as np
import joblib
import tensorflow as tf
from flask import Flask, jsonify, render_template
import threading

app = Flask(__name__)

# Load the saved model and scaler
model = tf.keras.models.load_model('router_location_model.h5')
scaler = joblib.load('scaler.pkl')

# Global variable to store the current coordinates
current_coordinates = {'x': 0, 'y': 0}

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

# Function to predict coordinates based on signal strengths
def predict_coordinates(router_values):
    # Scale the input values
    scaled_values = scaler.transform(np.array(router_values).reshape(1, -1))
    # Predict using the model
    prediction = model.predict(scaled_values)
    return prediction[0]

# Function to monitor selected routers and predict coordinates
def monitor_and_predict(routers):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]

    try:
        while True:
            iface.scan()  # Continuously scan for updated signal strengths
            time.sleep(3)  # Sleep for 3 seconds to let the scan complete
            networks = iface.scan_results()

            router_signals = []  # Store the signal strengths of the selected routers

            # Find the signal strength for the selected routers, if not found, set it to 0
            for router in routers:
                found = False
                for network in networks:
                    if network.ssid == router.ssid:
                        router_signals.append(network.signal)
                        found = True
                        break
                if not found:
                    router_signals.append(0)  # If router is not found, set signal strength to 0

            # Print the router signals
            print(f"\nSelected Router Signals: {router_signals}")

            # Predict coordinates based on the router signals
            predicted_coordinates = predict_coordinates(router_signals)
            current_coordinates['x'] = predicted_coordinates[0]
            current_coordinates['y'] = predicted_coordinates[1]
            print(f'Predicted Coordinates: x={predicted_coordinates[0]}, y={predicted_coordinates[1]}\n')

            print("Monitoring... Press Ctrl+C to stop.")
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/coordinates')
def coordinates():
    return jsonify({'x': float(current_coordinates['x']), 'y': float(current_coordinates['y'])})

if __name__ == "__main__":
    # Step 1: Scan available networks
    available_networks = scan_wifi()



    # Step 3: Start the scanning thread
    scan_thread = threading.Thread(target=monitor_and_predict, args=(choose_routers(available_networks),))
    scan_thread.daemon = True  # Allow the thread to be killed when the main program exits
    scan_thread.start()

    # Run the Flask app
    app.run(debug=True)
