import os
import glob
import csv
import zipfile

from os.path import basename
from transliterate import translit
from flask import Flask, render_template, request,  send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
UPLOAD_FOLDER = os.path.join(APP_STATIC, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# только .csv файлы
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# если .csv то сохранет во временный каталог "uploads"
def handle_file(f):
    if not allowed_file(f.filename):
        return
    filename = secure_filename(f.filename)
    print(filename)
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename


@app.route('/')
def home():
    return render_template('home.html')


# POST запрос с присланными данными
@app.route('/upload', methods=['POST'])
def upload():
    # удалить все данные из временных каталогов
    folders = [APP_STATIC+'/for_load/*', APP_STATIC+'/uploads/*', APP_STATIC+'/zip/*']
    for del_files in folders:
        files = glob.glob(del_files)
        for f in files:
            os.remove(f)

    # по имени с input длять файлы и сохранить во временный каталог
    files = request.files.getlist('file[]')
    if files:
        for file in files:
            handle_file(file)
    opener()
    # выгрузка обратно zip файла со всеми транлитерированными наборами данных
    uploads = APP_STATIC+'/zip/'
    return send_from_directory(directory=uploads, filename='files.zip')


def opener():
    dict_lines = {}

    # массив названий файлов для записи в zip файл
    files_name = []

    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        for file in files:
            files_name.append(file)
            with open(root+"/"+file, 'rt', encoding='utf-8') as r:
                spam_reader = csv.reader(r)
                n = 0
                for row in spam_reader:
                    if len(row) > 0:
                        # транслитерируем и записывам в dict
                        dict_lines[n] = translit(row[0], 'ru', reversed=True)
                        n += 1
            with open(APP_STATIC+'/for_load/'+file, "w", encoding='utf-8') as wr:
                # из dict пишем в новый .csv файл
                write_file = csv.writer(wr, quoting=csv.QUOTE_MINIMAL, delimiter=';')
                for line in dict_lines.values():
                    iter_line = line.split(';')
                    write_file.writerow(iter_line)
                dict_lines = {}
    # создаём zip файл со всеми изменёнными файлами
    with zipfile.ZipFile(APP_STATIC+'/zip/files.zip', 'w') as zip_file:
        for file in files_name:
            path = APP_STATIC+'/for_load/'+file
            zip_file.write(path, basename(path))

if __name__ == '__main__':
    app.run()

# файлам дописывается название папки потому что в home.html в input'е стоит  "webkitdirectory directory"