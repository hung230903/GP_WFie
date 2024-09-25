from flask import Flask, jsonify
import pywifi
import time
import numpy as np
import joblib
import tensorflow as tf
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

    # Scan for networks
    while True:
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


        # Find the signal strength for the selected routers
        for router in selected_routers:
            found = False
            for network in networks:
                if network.ssid == router.ssid:
                    router_signals.append(network.signal)
                    found = True
                    break
            if not found:
                router_signals.append(0)  # If router is not found, set signal strength to 0

        # Predict coordinates based on the router signals
        predicted_coordinates = predict_coordinates(router_signals)
        # Update the global coordinates variable
        current_coordinates['x'] = predicted_coordinates[0]
        current_coordinates['y'] = predicted_coordinates[1]
        print(f'Predicted Coordinates: x={current_coordinates["x"]}, y={current_coordinates["y"]}\n')

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

@app.route('/coordinates')
def coordinates():
    return jsonify(current_coordinates)

if __name__ == "__main__":
    # Step 1: Scan available networks
    available_networks = scan_wifi()

    # Step 2: Choose up to 4 routers to focus on
    focused_routers = choose_routers(available_networks)
    # Run the Flask app
    app.run(debug=True)
    
    # Start the scanning thread
    scan_thread = threading.Thread(target=scan_wifi)
    scan_thread.daemon = True  # Allow the thread to be killed when the main program exits
    scan_thread.start()

