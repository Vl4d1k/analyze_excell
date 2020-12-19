from flask import Flask, render_template, request, flash, redirect, url_for
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.ticker as mticker

# путь, куда будет загружен файл со статистикой
UPLOAD_FOLDER = '/app/files/'

app = Flask(__name__)
# установка пути для загрузки файла со статистикой
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# сработает при запросе 127.0.0.1/
@app.route('/', methods=['GET', 'POST'])
def hello_world():
  # возвращаем html-страницу из папки templates
  return render_template('index.html', name="index")

# сработает при запросе 127.0.0.1/analyze
@app.route('/analyze', methods=['GET', 'POST'])
def analyze_data():
      isGridVisible = True # рисовать сетку(True - с сеткой, False - без)
      # если метод запроса на сервер пост 
      if request.method == 'POST':
        # получаем файл от пользователя
        file = request.files['upload-file']
        # получаем относиткльный путь к файлу со статистикой
        relative_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        # получаем абсолютный путь для сохраннения
        absolute_path = os.getcwd() + relative_path
        # сохраняем файл со статистикой
        file.save(absolute_path)
        # считываем данные из excell-файла
        data = pd.read_excel(file)
        # проверяем нудно ли выводить сетку
        try:
          if(request.form['grid'] == 1):
            isGridVisible = True
        except:
          isGridVisible = False
        # получаем массив путей к графикам
        pictures = analyze_data(data, isGridVisible)
        # выводим html-страницу с графиками
        return render_template('data.html', data = pictures )

def analyze_data(data, isGridVisible):
  # получаем текущее время и дату
  datetime_str = datetime.now().strftime("%d_%m_%y_%H_%M_%S")
  # создаём путь для папки с графиками
  path_for_pics = os.getcwd() + '\\app\\static\\pictures\\' + datetime_str
  # создаем папку для графиков
  os.mkdir(path_for_pics)
  # создаём пустой массив путей к графикам
  pics = []

  # построим простой график

  # создаем область Figure
  plt.figure(figsize=(8,5), dpi= 80)
  # строим график
  plt.plot(data[data.keys()[0]], data[data.keys()[1]])
  # добавляем линии вспомогательной сетки
  plt.grid(isGridVisible)  
  # задаем названия для осей
  plt.gca().set(ylabel='Уровень сахара', xlabel='День')
  # к каждому значению шкалы на графике добавляем текст  
  plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f \n ммоль/л'))
  plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f день'))
  # сохраняем график
  plt.savefig(path_for_pics + '/simple.png')
  # добавляем ссылку на картинку в массив, чтобы потом отобразить на странице
  pics.append(url_for('static', filename= 'pictures/' + datetime_str + '/simple.png'))

  # гистограмма


  # создаем область Figure
  plt.figure(figsize=(8,5), dpi= 80)
  # добавляем линии вспомогательной сетки
  plt.grid(isGridVisible)
  # добавляем заголовок к графику
  plt.title('Гистограмма')
  # задаем названия для осей
  plt.gca().set(ylabel='Количество', xlabel='$Уровень сахара$')
  # строим гистограмму
  plt.hist(data[data.keys()[1]], density=True, bins=30)
  # к каждому значению шкалы на графике добавляем текст
  plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%f раз'))
  plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f \n ммоль/л'))
  # сохраняем график
  plt.savefig(path_for_pics + '/hist.png')
  # добавляем ссылку на картинку в массив, чтобы потом отобразить на странице
  pics.append(url_for('static', filename= 'pictures/' + datetime_str + '/hist.png'))


  # среднеее значение


  # создаем область Figure
  plt.figure(figsize=(8,5), dpi= 80)
  # задаем названия для осей
  plt.gca().set(ylabel='Уровень сахара', xlabel='')
  # строим график
  plt.boxplot([data[data.keys()[1]]])
  # добавляем линии вспомогательной сетки
  plt.grid(isGridVisible)
  # к каждому значению шкалы на графике добавляем текст
  plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%0.1f \n ммоль/л'))
  # сохраняем график
  plt.savefig(path_for_pics + '/boxplot.png')
  # добавляем ссылку на картинку в массив, чтобы потом отобразить на странице
  pics.append(url_for('static', filename= 'pictures/' + datetime_str + '/boxplot.png'))

  # дисперсия

  #  подготовка данных
  df = data
  x = df.loc[:, [data.keys()[1]]]
  df['mpg_z'] = (x - x.mean())/x.std()
  df['colors'] = ['red' if x < 0 else 'green' for x in df['mpg_z']]
  df.sort_values('mpg_z', inplace=True)
  df.reset_index(inplace=True)
  # создаем область Figure
  plt.figure(figsize=(8,5), dpi= 80)
  # создаем область Figure
  plt.hlines(y=df.index, xmin=0, xmax=df.mpg_z, color=df.colors, alpha=0.4, linewidth=5)
  # задаем названия для осей
  plt.gca().set(ylabel='Уровень сахара', xlabel='$Дисперсия$')
  plt.yticks(df[data.keys()[0]], df[data.keys()[1]], fontsize=12)
  plt.title('Порядок и величина дисперсии,', fontdict={'size':20})
  # задаем стиль для сетки
  if isGridVisible:
    plt.grid(linestyle='--', alpha=0.5)
  # к каждому значению шкалы на графике добавляем текст
  plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%d день'))
  # сохраняем график
  plt.savefig(path_for_pics + '/dispersia.png')
  # добавляем ссылку на картинку в массив, чтобы потом отобразить на странице
  pics.append(url_for('static', filename= 'pictures/' + datetime_str + '/dispersia.png'))
  
  #возвращаем массив ссылок на графики
  return pics



