import json
from flask import Flask, render_template, request, jsonify
import pyttsx3
from gtts import gTTS
import os
import speech_recognition as sr
from googletrans import Translator

# Initialize Flask App
app = Flask(__name__)

# Load responses and orders from JSON files with error handling
# Load responses and orders from JSON files with error handling
try:
    with open('responses.json', 'r', encoding='utf-8') as f:  # Specify UTF-8 encoding
        responses = json.load(f)
except FileNotFoundError:
    responses = {"fallback": "Sorry, I couldn't process your request right now. Please try again later."}
    print("Warning: 'responses.json' not found. Using default fallback response.")

file_path = "orders.json"
try:
    with open(file_path, "r", encoding='utf-8') as file:  # Specify UTF-8 encoding
        orders = json.load(file)
except FileNotFoundError:
    orders = {}
    print("Warning: 'orders.json' not found. Order details will not be available.")


# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Function to capture speech input
def capture_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for user input...")
        try:
            audio = recognizer.listen(source)
            # Convert speech to text
            user_speech = recognizer.recognize_google(audio, language="hi-IN")
            print(f"User said: {user_speech}")
            return user_speech
        except sr.RequestError as e:
            print(f"आवाज समझ नहीं आ रही: {e}")
            return "Sorry, I didn't catch that"

# Function to get response from the chatbot
def get_response(key):
    return responses.get(key, responses["fallback"])

# Function to process the order based on the order ID
def search_in_orders(search_query, orders):
    matching_records = []
    search_query = search_query.lower()  # Convert query to lowercase for case-insensitive search
    for order in orders:
        for value in order.values():
            if search_query in str(value).lower():
                matching_records.append(order)
                break
    return matching_records
            
# Route to serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# API endpoint to handle the user query
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['query'].strip()  # Get the query from frontend

    # Translate the user query to English if it's in Hindi
    translator = Translator()
    translated_query = translator.translate(user_input, src='hi', dest='en').text.lower()

    # Check if it's the first interaction (no previous query)
    if user_input.lower() == "":
        # Greet the user in Hindi if it's their first interaction
        response = "नमस्ते! मैं आपकी सहायता करने के लिए यहाँ हूँ। आप किस प्रकार की मदद चाहते हैं?"
    else:
        # Extract order ID (if present) and check if it's mentioned in the user's query
        if "order" in translated_query:
            order_id = None
            for word in translated_query.split():
                if word.isdigit():  # If it's a number, assume it's an order ID
                    order_id = word
                    break
         # Search orders based on the query
        search_results = search_in_orders(translated_query, orders)
        if search_results:
            response = "Matching orders found:\n" + "\n".join(
                [f"Order ID: {order['order_id']}, Status: {order['status']}" for order in search_results]
            )
        else:
            response = "कृपया एक वैध ऑर्डर आईडी प्रदान करें।"

    # Convert the response to speech
    bolo(response)

    # Return the response to the user
    return jsonify({"response": response})

# Function to speak out the response using gTTS
def bolo(text):
    tts = gTTS(text=text, lang='hi')
    tts.save("response.mp3")
    os.system("start response.mp3")

if __name__ == '__main__':
    app.run(debug=True)
