from flask import Flask, render_template, request
from database import import_DB

app = Flask("philscrapper")


@app.route('/')
def home():
    rows = import_DB()
    return render_template('home.html', rows=rows)

"""
@app.route('/find')
def find():
    word = request.args.get('word')
    if word:
        word = word.lower()
        nous = get_nous(word)
        # sort_nous = sorted(
        #    nous, key = lambda value: value['date'], reverse=True)
    return render_template('find.html', searchingBy=word, nous=nous)
"""

if __name__ == '__main__':
    app.run(debug=True)

