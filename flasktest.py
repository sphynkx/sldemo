## https://flask.palletsprojects.com/en/2.3.x/quickstart/
## run with cmd flask --app flask00.py run --debug --port=8080 --reload
## as http://127.0.0.1:8080/
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

## doesnt work
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4455)
