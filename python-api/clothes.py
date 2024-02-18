from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

# Sample cloth material names for classification
cloth_materials = {
    'high': ['cotton', 'linen'],
    'mid': ['silk', 'satin'],
    'low': ['wool', 'cashmere', 'flannel']
}

def extract_text_from_image(image):
    """
    Function to extract text from an image using Tesseract OCR.
    """
    try:
        img = Image.open(BytesIO(image))
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return str(e)

def classify_cloth_material(text):
    """
    Function to classify cloth material based on keywords in the extracted text.
    Returns a dictionary containing the percentage of matches for each classification category.
    """
    material_matches = {'high': 0, 'mid': 0, 'low': 0}
    total_matches = 0
    for material, keywords in cloth_materials.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                material_matches[material] += 1
                total_matches += 1

    classification_percentages = {}
    for material, count in material_matches.items():
        percentage = (count / total_matches) * 100 if total_matches > 0 else 0
        classification_percentages[material] = round(percentage, 2)

    return classification_percentages

@app.route('/classify_image', methods=['POST'])
def classify_image():
    """
    API endpoint to extract text from an image, classify cloth material, and return the classification percentages.
    """
    if request.is_json:
        data = request.get_json()
        if 'image_url' in data:
            image_url = data['image_url']
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    image = response.content
                    text = extract_text_from_image(image)
                    classification_percentages = classify_cloth_material(text)
                    return jsonify({'classification_percentages': classification_percentages})
                else:
                    return jsonify({'error': 'Failed to fetch image from URL'}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Missing image_url parameter in JSON'}), 400
    else:
        return jsonify({'error': 'Request data must be in JSON format'}), 400

if __name__ == '__main__':
    app.run(debug=True)
