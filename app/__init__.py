from flask import Flask, render_template, request, flash, redirect, url_for
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.ticker as mticker 

UPLOAD_FOLDER = '/app/files/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def hello_world():
  return render_template('index.html', name="index")

@app.route('/analyze', methods=['GET', 'POST'])
def analyze_data():
      isGridVisible = True
      if request.method == 'POST':
        #получаем файл
        file = request.files['upload-file']

        #относиткльный путь к файлу
        relative_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        #получаем абсолютный путь для сохраннения
        absolute_path = os.getcwd() + relative_path

        #сохраняем файл со статистикой
        file.save(absolute_path)
        data = pd.read_excel(file)
        #нужно ли вывети сетку
        try:
          if(request.form['grid'] == 1):
            isGridVisible = True
        except:
          isGridVisible = False

        #получаем массив путей к файлам
        pictures = analyze_data(data, isGridVisible)
        return render_template('data.html', data = pictures )

def analyze_data(data, isGridVisible):

  datetime_str = datetime.now().strftime("%d_%m_%y_%H_%M_%S")

  path_for_pics = os.getcwd() + '\\app\\static\\pictures\\' + datetime_str

  os.mkdir(path_for_pics)

  #массив путей к графикам
  pics = []

  #простой график

  plt.figure()
  plt.plot(data[data.keys()[0]], data[data.keys()[1]])
  plt.grid(isGridVisible)   # линии вспомогательной сетки
  plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f \n ммоль/л'))
  plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f день'))
  plt.savefig(path_for_pics + '/simple.png')
  pics.append(url_for('static', filename= 'pictures/' + datetime_str + '/simple.png'))

  #гистограмма

  plt.figure()
  plt.grid(isGridVisible)
  plt.title('Гистограмма')
  plt.hist(data[data.keys()[1]])
  plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f раз'))
  plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f \n ммоль/л'))
  plt.savefig(path_for_pics + '/hist.png')
  pics.append(url_for('static', filename= 'pictures/' + datetime_str + '/hist.png'))


  #среднеее значение

  plt.figure()
  plt.boxplot([data[data.keys()[1]]])
  plt.grid(isGridVisible)
  plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%0.1f \n ммоль/л'))
  plt.savefig(path_for_pics + '/boxplot.png')
  pics.append(url_for('static', filename= 'pictures/' + datetime_str + '/boxplot.png'))

  #дисперсия

  # подготовка данных
  df = data
  x = df.loc[:, [data.keys()[1]]]
  df['mpg_z'] = (x - x.mean())/x.std()
  df['colors'] = ['red' if x < 0 else 'green' for x in df['mpg_z']]
  df.sort_values('mpg_z', inplace=True)
  df.reset_index(inplace=True)

  plt.figure(figsize=(8,5), dpi= 80)
  plt.hlines(y=df.index, xmin=0, xmax=df.mpg_z, color=df.colors, alpha=0.4, linewidth=5)

  plt.gca().set(ylabel='Уровень сахара', xlabel='$Дисперсия$')
  plt.yticks(df[data.keys()[0]], df[data.keys()[1]], fontsize=12)
  plt.title('Порядок и величина дисперсии,', fontdict={'size':20})
  plt.grid(linestyle='--', alpha=0.5)
  plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%d день'))
  plt.savefig(path_for_pics + '/dispersia.png')
  pics.append(url_for('static', filename= 'pictures/' + datetime_str + '/dispersia.png'))
  
  return pics



