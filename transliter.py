import os
import glob
import csv
import zipfile

from transliterate import translit, get_available_language_codes
from flask import Flask, render_template, request, redirect, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
UPLOAD_FOLDER = os.path.join(APP_STATIC, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def handle_file(f):
    if not allowed_file(f.filename):
        return
    filename = secure_filename(f.filename)
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/upload', methods=['POST'])
def upload():
    folders = [APP_STATIC+'/for_load/*', APP_STATIC+'/uploads/*', APP_STATIC+'/zip/*']
    for del_files in folders:
        files = glob.glob(del_files)
        for f in files:
            os.remove(f)

    files = request.files.getlist('file[]')
    if files:
        for file in files:
            handle_file(file)
    return redirect('/open', code=200)


@app.route('/open')
def opener():


    dict = {}
    files_name = []
    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        for file in files:
            files_name.append(file)
            with open(root+"/"+file, 'rt', encoding='utf-8') as r:
                spam_reader = csv.reader(r)
                n = 0
                for row in spam_reader:
                    if len(row) > 0:
                        dict[n] = translit(row[0], 'ru', reversed=True)
                        n += 1
            with open(APP_STATIC+'/for_load/'+file, "w") as wr:
                write_file = csv.writer(wr, quoting=csv.QUOTE_MINIMAL, delimiter=';')
                for line in dict.values():
                    iter_line = line.split(';')
                    write_file.writerow(iter_line)
                dict = {}
    uploads = APP_STATIC+'/zip/'
    with zipfile.ZipFile(APP_STATIC+'/zip/files.zip', 'w') as zip_file:
        for file in files_name:
            zip_file.write(APP_STATIC+'/for_load/'+file)

    return send_from_directory(directory=uploads, filename='files.zip')

if __name__ == '__main__':
    app.run()
