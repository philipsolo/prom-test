from flask import Flask, request, render_template

# Flask constructor
app = Flask(__name__)


# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods=["GET", "POST"])
def gfg():
    if request.method == "POST":
        t =  request.form
        free_text = request.form.get("text")
        print(free_text)

    return render_template("form.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)