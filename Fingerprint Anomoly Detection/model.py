# Train and save the anomaly detection model
from sklearn.ensemble import IsolationForest
import pandas as pd
import joblib

# Example dataset with features like IP, user agent, and login time
data = pd.DataFrame({
    'ip_address': [12345, 67890, 12345, 67890],
    'user_agent': [1, 2, 1, 3],
    'login_time': [10, 20, 15, 25]
})

# Train the Isolation Forest model
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(data)

# Save the model to a file
joblib.dump(model, 'anomaly_detection_model.pkl')