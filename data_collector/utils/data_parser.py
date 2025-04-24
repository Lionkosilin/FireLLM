import random
import json

def generate_sensor_data():
    return json.dumps({
        'temperature': round(random.uniform(20.0, 40.0), 2),
        'humidity': round(random.uniform(30.0, 90.0), 2),
        'smoke': round(random.uniform(0.0, 1.0), 3)
    })