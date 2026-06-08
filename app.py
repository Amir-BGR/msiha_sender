from flask import Flask, request
from flask_cors import CORS # این خط را اضافه کنید
import os
import requests
from instagrapi import Client

app = Flask(__name__)
CORS(app) # این خط را اضافه کنید تا CORS فعال شود

# ایجاد کلاینت اینستاگرام
cl = Client()
# لاگین با استفاده از متغیرهای محیطی که در Render تنظیم کردید
cl.login(os.getenv('INSTA_USER'), os.getenv('INSTA_PASSWORD'))

@app.route('/healthz')
def health():
    return "OK", 200

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    img_url = data.get('image_url')
    caption = data.get('caption')
    
    if not img_url or not caption:
        return {"status": "error", "message": "Missing data"}, 400

    try:
        # ۱. دانلود عکس از لینک ارسالی وردپرس
        response = requests.get(img_url)
        with open('temp.jpg', 'wb') as f:
            f.write(response.content)
            
        # ۲. آپلود در اینستاگرام
        cl.photo_upload('temp.jpg', caption)
        
        return {"status": "success", "message": "Post uploaded successfully"}, 200
        
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    app.run()
