from flask import Flask, render_template, redirect

app = Flask(__name__)

TOTAL_TABS = 20


@app.route("/")
def home():
    return redirect("/tab/1")


@app.route("/tab/<int:number>")
def tab(number):
    if number < 1 or number > TOTAL_TABS:
        return redirect("/tab/1")

    return render_template(
        "page.html",
        current=number,
        tabs=range(1, TOTAL_TABS + 1),
    )


if __name__ == "__main__":
    app.run(debug=True)