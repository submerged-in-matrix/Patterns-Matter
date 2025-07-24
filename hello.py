from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Hallo! Los geht!"
if __name__ == "__main__":
    app.run(debug=True)
# To run this Flask application, save it as hello.py and execute it with Python.