import requests
from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import tensorflow as tf
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://10.30.2.252:52990"}})

# Global variable to store the result
result = {}




# Load your trained  model
model = tf.keras.models.load_model('model.h5')

# Define a list of class labels (disease names)
class_labels = ["Tomato Bacterial spot", "Tomato Early blight", "Tomato Late blight", "Tomato healthy"]

# Define the input image size expected by your model
input_image_size = (224, 224)  # Adjust this size based on your model's input requirements

# Define the URL of your Spring Boot API
spring_boot_api_url = "http://10.30.2.252:8080/api/v1/auth/diseaseName"  # Update with your Spring Boot API URL

# Define an API endpoint to receive images and make predictions
@app.route('/predict', methods=['POST'])
def predict_disease():
    global result
    try:
        # Get the image from the request
        image_file = request.files['image']

        # Check if the image file exists
        if image_file:
            # Preprocess the image (resize, normalize, etc.) to match your model's input size
            image = Image.open(image_file)
            image = image.resize(input_image_size)
            image = np.array(image) / 255.0  # Normalize pixel values

            # Make a prediction using the loaded VGGNet model
            prediction = model.predict(np.expand_dims(image, axis=0))

            # Get the predicted class label
            predicted_class_index = np.argmax(prediction)
            predicted_class = class_labels[predicted_class_index]
            probability_percentage = prediction[0][predicted_class_index] * 100  # Convert to percentage

            # Return the prediction result as JSON with class name and probability
            result = {'prediction': predicted_class, 'probability_percentage': probability_percentage,'predictedLabel': predicted_class}

            # Send the result label to your Spring Boot API
            send_result_to_spring_boot(result)

            return jsonify(result)

        else:
            return jsonify({'error': 'Image not found in request'})
    except Exception as e:
        return jsonify({'error': str(e)})
    
    
# Define an API endpoint to get the predicted label
@app.route('/get-predicted-label', methods=['GET'])
def get_predicted_label():
    try:
        # Logic to retrieve and return the predictedLabel
        # You can return it as JSON or plain text
        predicted_label = result.get('prediction')
 # Retrieve the predicted label from query parameters

        return jsonify({'predictedLabel': predicted_label})
    except Exception as e:
        return jsonify({'error': str(e)})
    


def send_result_to_spring_boot(result):
    try:
        response = requests.post(spring_boot_api_url, json=result)
        if response.status_code == 200:
            print("Result label sent to Spring Boot API successfully.")
        else:
            print("Failed to send result label to Spring Boot API. Status code:", response.status_code)
    except Exception as e:
        print("Error sending result label to Spring Boot API:", str(e))


if __name__ == '__main__':
    app.run(host='10.30.2.252', port=5000, debug=True)
