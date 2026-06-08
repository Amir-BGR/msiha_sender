from flask import Flask, request
from flask_cors import CORS
import os
import requests
import threading
from instagrapi import Client

app = Flask(__name__)
CORS(app)

# ایجاد و لاگین کلاینت اینستاگرام
cl = Client()
try:
    cl.login(os.getenv('INSTA_USER'), os.getenv('INSTA_PASSWORD'))
    # ذخیره تنظیمات برای جلوگیری از لاگین مجدد در هر درخواست
    cl.dump_settings("session.json")
except Exception as e:
    print(f"Login failed: {e}")

@app.route('/healthz')
def health():
    return "OK", 200

def async_upload(img_url, caption):
    """تابع پس‌زمینه برای انجام آپلود"""
    try:
        response = requests.get(img_url, stream=True)
        filename = 'temp.jpg'
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # آپلود در اینستاگرام
        cl.photo_upload(filename, caption)
        
        # حذف فایل پس از آپلود
        if os.path.exists(filename):
            os.remove(filename)
            
        print("Post uploaded successfully!")
    except Exception as e:
        print(f"Error in async_upload: {e}")

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    img_url = data.get('img_url')
    caption = data.get('caption')
    
    if not img_url:
        return {"status": "error", "message": "No image URL provided"}, 400

    # شروع عملیات آپلود در یک ترد جداگانه
    thread = threading.Thread(target=async_upload, args=(img_url, caption))
    thread.start()
    
    return {"status": "success", "message": "عملیات آپلود در پس‌زمینه شروع شد."}, 200

if __name__ == '__main__':
    # استفاده از port مشخص شده توسط رندر یا پیش‌فرض ۵۰۰۰
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
