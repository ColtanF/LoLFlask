from flask import Flask, render_template, request
from threading import Thread
import RiotAPI

app = Flask(__name__)

buttonPressed = 0

@app.route('/', methods=["GET", "POST"])
def home():
    matchFound = True
    global buttonPressed
    matchInfo = None
    print("buttonPressed: " + str(buttonPressed))
    buttonPressed += 1
    if request.method == "POST" and buttonPressed > 1:
        summToSearch = request.form['searchTerm']
        if summToSearch != "":
            results = RiotAPI.search(summToSearch)
            if results:
                matchInfo = results
            else:
                matchFound = False
                matchInfo = None
    return render_template("home.html", presses = buttonPressed, matchInfo=matchInfo, matchFound = matchFound)

@app.route("/coltan")
def coltan():
    return "Hello, Coltan!"

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
