from flask import Flask, render_template, request

from main import compile_minic

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():

    result = None
    code = ""

    if request.method == 'POST':

        code = request.form['code']

        result = compile_minic(code)

    return render_template(
        'index.html',
        result=result,
        code=code
    )


if __name__ == '__main__':

    app.run(debug=True)