from sqlalchemy import Column, Integer, TEXT, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, request
import requests
import sqlite3

engine = create_engine('sqlite:///hh_orm.sqlite', echo=True)

Base = declarative_base()


class Hh_parser(Base):
    __tablename__ = 'hh_key_skills'
    id = Column(Integer, primary_key=True)
    name = Column(TEXT)
    quality = Column(Integer)

    def __init__(self, name, quality):
        self.name = name
        self.quality = quality


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

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
        for i in result['key_skills']:
            if i['name'] in skills:
                skills[i['name']] += 1
            else:
                skills[i['name']] = 1
            sum_all_skills += 1
    result_sort = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    session = Session()
    for skill in result_sort:
        hh_key_skills = Hh_parser(skill[0], skill[1])
        session.add(hh_key_skills)
    session.commit()
    # вывод данных таблицы в терминал
    hh_key_skills_query = session.query(Hh_parser).all()
    for key_skills in hh_key_skills_query:
        print(key_skills.name, key_skills.quality)

    conn = sqlite3.connect('hh_orm.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT * from hh_key_skills')
    result_database = cursor.fetchall()
    try:
        average_salary = round(sum(salary) / len(salary), 2)
    except ZeroDivisionError:
        average_salary = 'Нет данных о зарплате'
    return render_template('results.html', salary=average_salary, vacancy=vacancy, data=result_database, area=area)


app.run(debug=True)
