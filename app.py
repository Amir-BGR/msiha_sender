from flask import Flask, request
from flask_cors import CORS
import os
import requests
from instagrapi import Client

app = Flask(__name__)
CORS(app)

#  لاگین
cl = Client()
try:
    cl.login(os.getenv('INSTA_USER'), os.getenv('INSTA_PASSWORD'))
except Exception as e:
    print(f"Login failed: {e}")

@app.route('/healthz')
def health():
    return "OK", 200

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    img_url = data.get('img_url') # دقت کنید در وردپرس img_url بود
    caption = data.get('caption')
    
    if not img_url:
        return {"status": "error", "message": "No image URL"}, 400

    # در فایل app.py کد آپلود را اینگونه اصلاح کنید:
try:
    response = requests.get(img_url, stream=True) # اضافه کردن stream=True
    with open('temp.jpg', 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    cl.photo_upload('temp.jpg', caption)
    
    # حذف فایل بعد از آپلود برای آزاد شدن حافظه
    if os.path.exists('temp.jpg'):
        os.remove('temp.jpg')
        
    return {"status": "success", "message": "Post uploaded!"}, 200

if __name__ == '__main__':
    app.run()
