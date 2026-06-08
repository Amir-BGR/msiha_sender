from flask import Flask, request
import os
from instagrapi import Client

app = Flask(__name__)

@app.route('/healthz')
def health():
    return "OK", 200

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    # کد instagrapi اینجا قرار می‌گیرد
    return {"status": "success", "received": data.get('title')}, 200

if __name__ == '__main__':
    app.run()