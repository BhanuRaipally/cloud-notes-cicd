import os
from flask import Flask, jsonify

app = Flask(__name__)
APP_VERSION = os.getenv("APP_VERSION", "local")

@app.get("/")
def home():
    return f"""
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Cloud Notes Status</title>
    <style>
      body {{ font-family: Arial, sans-serif; max-width: 760px; margin: 4rem auto; padding: 0 1rem; background: #f3f6fb; color: #172033; }}
      main {{ background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 8px 24px #17203318; }}
      .ok {{ color: #137547; font-weight: bold; }}
      code {{ background: #eef2f8; padding: .2rem .4rem; border-radius: 5px; }}
    </style></head>
    <body><main>
      <h1>Cloud Notes — Deployment Status</h1>
      <p class="ok">● Application is running</p>
      <p>Version: <code>{APP_VERSION}</code></p>
      <p>CI/CD practice: GitHub → CodePipeline → CodeBuild → S3 → CodeDeploy → EC2</p>
      <p>Health endpoint: <a href="/health">/health</a></p>
    </main></body></html>
    """

@app.get("/health")
def health():
    return jsonify(status="ok", version=APP_VERSION), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
