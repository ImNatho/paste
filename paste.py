from flask import Flask, request, redirect, url_for
from pymongo import MongoClient
import os, random, string

app = Flask(__name__)
mongo_client = MongoClient(os.environ['MONGO_URI'])
db = mongo_client.paste
pastes_col = db.pastes


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        key = generate_key()
        pastes_col.insert_one({
            "key": key,
            "data": request.form['paste_data'].replace('\n', '\\n')
        })
        return redirect(url_for('get_paste', key=key))
    return '''
        <h1>Create a paste</h1>
        <p><a href="/list">List Pastes</a></p><br>
        <form action="/" method="post">
            <textarea style="resize: none;" cols="200" rows="50" name="paste_data"></textarea>
            <input type="submit" value="Paste" />
        </form>
    '''


@app.route('/<key>')
def get_paste(key):
    paste = pastes_col.find_one({"key": key})
    if paste:
        return "<pre>" + str(html_escape(paste['data']).replace('\\n', '\n')) + "</pre>"
    return 'No paste "%s" found!' % key, 404


@app.route('/list')
def list_pastes():
    builder = "<a href='" + url_for('index') + "'>Home</a><br>" \
              "<h2>Current pastes:</h2><br>"
    cursor = pastes_col.find()
    for paste in cursor:
        builder += "<a href='" + url_for('get_paste', key=paste['key']) + "'>" + paste['key'] + "</a><br>"
    return builder


def generate_key():
    while True:
        key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        cursor = pastes_col.find({"key": key})
        if cursor.count() == 0:
            return key


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }


def html_escape(text):
    return "".join(html_escape_table.get(c, c) for c in text)


if __name__ == '__main__':
    app.run()
