from flask import Flask, request
from flask_cors import CORS
import os
import requests
import threading
from instagrapi import Client

app = Flask(__name__)
CORS(app)

# ایجاد کلاینت اینستاگرام
cl = Client()

def login_instagram():
    """تابع مدیریت لاگین با پشتیبانی از 2FA"""
    username = os.getenv('INSTA_USER')
    password = os.getenv('INSTA_PASSWORD')
    verification_code = os.getenv('VERIFICATION_CODE')
    
    try:
        if verification_code:
            # لاگین با کد تایید
            cl.login(username, password, verification_code=verification_code)
        else:
            # لاگین معمولی
            cl.login(username, password)
        
        # ذخیره نشست برای استفاده‌های بعدی
        cl.dump_settings("session.json")
        print("Login successful!")
    except Exception as e:
        print(f"Login failed: {e}")

# اجرای لاگین در شروع برنامه
login_instagram()

@app.route('/healthz')
def health():
    return "OK", 200

def async_upload(img_url, caption):
    """آپلود در پس‌زمینه"""
    try:
        response = requests.get(img_url, stream=True)
        filename = 'temp.jpg'
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        cl.photo_upload(filename, caption)
        
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
        return {"status": "error", "message": "No image URL"}, 400

    thread = threading.Thread(target=async_upload, args=(img_url, caption))
    thread.start()
    
    return {"status": "success", "message": "عملیات شروع شد."}, 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
