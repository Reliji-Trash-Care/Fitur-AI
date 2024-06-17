from flask import Flask, request, jsonify
import tensorflow as tf
from PIL import Image
import numpy as np
from keras.models import load_model

app = Flask(__name__)

# Load the model without custom objects
model = load_model("model.h5")

# Label dan handling instructions
label_mapping = {
    0: "baterai",
    1: "biologis",
    2: "gelas",
    3: "kardus",
    4: "kertas",
    5: "metal",
    6: "pakaian",
    7: "plastik",
    8: "sepatu",
}

category_mapping = {
    "baterai": "anorganik",
    "biologis": "organik",
    "gelas": "anorganik",
    "kardus": "anorganik",
    "kertas": "anorganik",
    "metal": "anorganik",
    "pakaian": "anorganik",
    "plastik": "anorganik",
    "sepatu": "anorganik",
}

handling_instructions = {
    "baterai": """Baterai adalah sampah anorganik berbahaya yang mengandung bahan kimia beracun. Pengelolaannya harus dilakukan dengan hati-hati untuk menghindari kerusakan lingkungan.
- Kumpulkan baterai bekas di wadah terpisah.
- Jangan membuangnya bersama sampah rumah tangga.
- Bawa ke titik pengumpulan atau fasilitas daur ulang khusus untuk baterai.""",

    "biologis": """Sampah biologis atau organik adalah sisa-sisa bahan alami yang dapat terurai. Contohnya termasuk sisa makanan, daun, dan bahan taman.
- Kumpulkan sampah organik di tempat sampah khusus organik.
- Sampah organik bisa dikomposkan untuk menghasilkan pupuk alami.
- Hindari mencampur sampah organik dengan sampah anorganik untuk memudahkan proses pengomposan.""",

    "gelas": """Gelas adalah sampah anorganik yang dapat didaur ulang menjadi produk baru.
- Bersihkan gelas dari sisa makanan atau minuman.
- Pisahkan gelas berdasarkan warnanya jika memungkinkan.
- Bawa ke fasilitas daur ulang gelas atau letakkan di tempat sampah daur ulang gelas.""",

    "kardus": """Kardus adalah sampah anorganik yang terbuat dari serat kayu dan mudah didaur ulang.
- Lipat kardus agar tidak memakan banyak tempat.
- Pastikan kardus dalam keadaan bersih dan kering.
- Bawa ke fasilitas daur ulang kertas atau letakkan di tempat sampah daur ulang kertas.""",

    "kertas": """Kertas adalah sampah anorganik yang dapat didaur ulang menjadi produk kertas baru.
- Lipat atau gunting kertas agar lebih mudah diolah.
- Pastikan kertas dalam keadaan bersih dan kering.
- Bawa ke fasilitas daur ulang kertas atau letakkan di tempat sampah daur ulang kertas.""",

    "metal": """Metal adalah sampah anorganik yang dapat didaur ulang menjadi produk metal baru.
- Bersihkan metal dari sisa makanan atau bahan lainnya.
- Pisahkan metal berdasarkan jenisnya jika memungkinkan.
- Bawa ke fasilitas daur ulang metal atau letakkan di tempat sampah daur ulang metal.""",

    "pakaian": """Pakaian adalah sampah anorganik yang dapat didaur ulang atau digunakan kembali.
- Jika pakaian masih layak pakai, donasikan ke panti asuhan atau lembaga sosial.
- Jika tidak layak pakai, bawa ke fasilitas daur ulang tekstil.
- Pisahkan pakaian berdasarkan jenis kain jika memungkinkan.""",

    "plastik": """Plastik adalah sampah anorganik yang sangat sulit terurai tetapi dapat didaur ulang menjadi produk baru.
- Bersihkan plastik dari sisa makanan atau bahan lainnya.
- Pisahkan plastik berdasarkan jenisnya jika memungkinkan.
- Bawa ke fasilitas daur ulang plastik atau letakkan di tempat sampah daur ulang plastik.""",

    "sepatu": """Sepatu adalah sampah anorganik yang dapat didaur ulang atau digunakan kembali.
- Jika sepatu masih layak pakai, donasikan ke panti asuhan atau lembaga sosial.
- Jika tidak layak pakai, bawa ke fasilitas daur ulang tekstil.
- Pisahkan sepatu berdasarkan bahan pembuatannya jika memungkinkan.""",
}

# Function to check and convert image to RGB format if necessary
def preprocess_image(file):
    try:
        img = Image.open(file.stream)
        
        # Convert to RGB if image is in RGBA format
        if img.mode == "RGBA":
            img = img.convert("RGB")
        
        img = img.resize((224, 224))  # Resize to expected input size
        img = np.array(img) / 255.0  # Normalize pixel values
        
        # Ensure image has 3 channels (RGB)
        if img.shape[-1] != 3:
            return None, {"error": "Expected RGB image with 3 channels"}
        
        img = np.expand_dims(img, axis=0)  # Add batch dimension
        return img, None
    
    except Exception as e:
        return None, {"error": str(e)}


@app.route("/")
def hello_world():
    return {"status": "SUCCESS", "message": "Service is running"}, 200


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        img, preprocess_error = preprocess_image(file)
        
        if preprocess_error:
            return jsonify(preprocess_error), 400

        # Perform prediction with the model
        prediction = model.predict(img)
        predicted_class = np.argmax(prediction, axis=1)[0]
        label = label_mapping[predicted_class]
        category = category_mapping[label]
        instructions = handling_instructions[label]

        return jsonify({
            "label": label,
            "category": category,
            "handling_instructions": instructions
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)