import tensorflow as tf
import numpy as np
import joblib
import argparse

# Load the saved model
model = tf.keras.models.load_model('router_location_model.h5')

# Load the scaler
scaler = joblib.load('scaler.pkl')

# Function to predict x, y based on router input values
def predict_coordinates(router_values):
    # Scale the input values
    scaled_values = scaler.transform(np.array(router_values).reshape(1, -1))
    # Predict using the model
    prediction = model.predict(scaled_values)
    return prediction[0]

# Main function to handle command-line input
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Predict x and y coordinates based on router signal strengths.')
    parser.add_argument('signals', type=float, nargs=4, help='Signal strengths from 4 routers (in dBm).')
    
    args = parser.parse_args()
    
    # Get router input values
    router_input = args.signals
    
    # Predict the coordinates
    predicted_coordinates = predict_coordinates(router_input)
    print(f'Predicted Coordinates: x={predicted_coordinates[0]}, y={predicted_coordinates[1]}')
