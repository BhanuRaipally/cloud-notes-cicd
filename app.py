import os
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
APP_VERSION = os.getenv("APP_VERSION", "local-dev")

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DevOps Status Dashboard</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 760px; margin: 4rem auto; padding: 0 1rem; background: #f5f7fb; color: #172033; }
    .card { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 8px 28px #17203314; }
    .ok { color: #137547; font-weight: 700; }
    code { background: #eef2f8; padding: .2rem .4rem; border-radius: 5px; }
  </style>
</head>
<body>
  <main class="card">
    <h1>DevOps Status Dashboard</h1>
    <p class="ok">● Application is running</p>
    <p>Deployment version: <code>{{ version }}</code></p>
    <p>CI/CD practice project: GitHub → CodePipeline → CodeBuild → S3 artifact → CodeDeploy → EC2</p>
    <p>Health check: <a href="/health">/health</a></p>
  </main>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(PAGE, version=APP_VERSION)

@app.get("/health")
def health():
    return jsonify(status="ok", version=APP_VERSION), 200

if __name__ == "__main__":
    # For local practice only. Production-like EC2 runs this through systemd/gunicorn.
    app.run(host="127.0.0.1", port=5000, debug=False)
