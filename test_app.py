"""Test if Flask can import and run"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Test OK - Flask is working!"

@app.route('/health')
def health():
    return "Healthy"

if __name__ == '__main__':
    print("Routes registered:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule}")
