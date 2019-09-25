import json

from flask import Flask, request
from flask_cors import CORS
import SaveInDB
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'venv//downloads//uploaded'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/api/ads", methods = ['POST', 'GET'])
def getData():
    import SaveInDB
    if request.method == 'POST':
        req_json = request.get_json();
        path = req_json['ad_path']
        zipCode = req_json['zipcode']
        adCategory = req_json['ad_type']
        textContent = req_json['text_content']
        location = req_json['location']

        SaveInDB.saveData(path, zipCode, adCategory, textContent, location)
        return "It works!"

    if request.method == 'GET':
        group_name = request.args.get('dataBy')
        print(group_name)
        return json.dumps(SaveInDB.fetchData(group_name))


@app.route("/api/stream", methods = ['GET'])
def streamAds():
    zipcode = request.args.get('zipcode')
    return SaveInDB.weather_category(zipcode)

@app.route("/api/uploadFile", methods = ['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        response = app.response_class(
            response=json.dumps("downloads//uploaded//" + filename),
            status=200,
            mimetype='application/json'
        )
        return response

if __name__ == "__main__":
    app.run(host='0.0.0.0')