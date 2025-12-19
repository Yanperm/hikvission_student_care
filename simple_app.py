from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('features.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Student Care System is running'})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)