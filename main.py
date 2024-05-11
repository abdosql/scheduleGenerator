from flask import Flask, request, jsonify

app = Flask(__name__)



@app.route("/")
def home_view():
        return "<h1>Welcome to Geeks for Geeks</h1>"


if __name__ == '__main__':
    app.run(debug=False)
