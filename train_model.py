import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import joblib

# Load training and testing data
train_data = pd.read_excel('dataTrain.xlsx')
test_data = pd.read_excel('dataTest.xlsx')

# Prepare training data
X_train = train_data[['router_dbm_1', 'router_dbm_2', 'router_dbm_3', 'router_dbm_4']].values
y_train = train_data[['x', 'y']].values

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Define and compile the model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(4,)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(2)
])

model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X_train_scaled, y_train, epochs=100, verbose=1)

# Save the model
model.save('router_location_model.h5')
# Save the scaler
joblib.dump(scaler, 'scaler.pkl')

# Evaluate the model (optional)
X_test = test_data[['router_dbm_1', 'router_dbm_2', 'router_dbm_3', 'router_dbm_4']].values
y_test = test_data[['x', 'y']].values
X_test_scaled = scaler.transform(X_test)

test_loss = model.evaluate(X_test_scaled, y_test)
print(f'Test Loss: {test_loss}')
