from flask import Flask, render_template, request
import requests
import sqlite3


DOMAIN = 'https://api.hh.ru/'


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contacts/')
def contacts():
    developer_name = 'Sharov Igor'
    developer_phone_number = '123456789'
    developer_mail = 'igor@sharov.ru'
    return render_template('contacts.html', name=developer_name, phone=developer_phone_number, mail=developer_mail)


@app.route('/results/', methods=['POST'])
def run_post_vacancy():
    # Как получть данные формы
    vacancy = request.form['vacancy']
    area = request.form['area']
    # по умолчанию - python developer
    if not vacancy:
        vacancy = 'python developer'
    if not area:
        area = 1
    url = f'{DOMAIN}vacancies'
    params = {
        'text': vacancy,
        'area': area,
        'period': 30,  # поставил период за 30 дней
        'page': 10  # не совсем понял смысл этих страниц
    }

    skills = {}
    sum_all_skills = 0
    sum_item = 0
    salary = []

    result = requests.get(url, params=params).json()
    items = result['items']
    found = result['found']

    for item in items:
        url = item['url']
        result = requests.get(url).json()
        # считаю только вакансии с ключевыми навыками
        if result['key_skills']:
            sum_item += 1
        # считаю только вакансии с данными по з/п, от минимального значения
        if result['salary']:
            val = item['salary']
            if val['from']:
                salary.append(val['from'])
        # time.sleep(3)
        # не помогла задержка, все равно 20 вакансий только показывает
        for i in result['key_skills']:
            if i['name'] in skills:
                skills[i['name']] += 1
            else:
                skills[i['name']] = 1
            sum_all_skills += 1
    result_sort = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    conn = sqlite3.connect('hh.sqlite')
    cursor = conn.cursor()
    cursor.execute("insert into vacancy (name_vacancy) VALUES (?)", (vacancy, ))
    cursor.execute("insert into id_region (id_region) VALUES (?)", (area, ))
    for skill in result_sort:
        cursor.execute("insert into key_skills (name, quality) VALUES (?, ?)", (skill[0], skill[1]))
    conn.commit()
    cursor.execute('SELECT * from key_skills')
    result_database = cursor.fetchall()
    try:
        average_salary = round(sum(salary) / len(salary), 2)
    except ZeroDivisionError:
        average_salary = 'Нет данных о зарплате'
    return render_template('results.html', salary=average_salary, vacancy=vacancy, data=result_database, area=area)


app.run(debug=True)
