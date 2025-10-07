from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

def extract_fields(text):
    # Use the same extract_fields logic from the previous response
    # (Insert your extract_fields function here)
    pass

@app.route('/extract', methods=['POST'])
def extract():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    image_file = request.files['image']
    img = Image.open(image_file.stream)
    text = pytesseract.image_to_string(img)
    fields = extract_fields(text)
    return jsonify(fields)

if __name__ == '__main__':
    app.run(debug=True)
