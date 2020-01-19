import requests
import json
import time
import pprint

DOMAIN = 'https://api.hh.ru/'

url = f'{DOMAIN}vacancies'
vacancy = input('Введите вакансию для поиска (по умолчанию - python developer): ')
if not vacancy:
    vacancy = 'python developer'
area = input('Введите регион для поиска (по умолчанию - Москва): ')
if not area:
    area = '1'


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
requirements = []

result = requests.get(url, params=params).json()
items = result['items']
found = result['found']
print(f'Вакансий найдено: {found}', '\n')
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
average_salary = round(sum(salary) / len(salary), 2)

for k, v in result_sort:
    for_file = {'name': k, 'count': v, 'percent': round(v / sum_all_skills * 100, 2)}
    requirements.append(for_file)
    file_name = str(vacancy)
    file = {'keywords': vacancy, 'count': sum_all_skills, 'average_salary': average_salary,
            'requirements': requirements}
    with open(file_name + '.json', 'w', encoding='utf-8') as f:
        json.dump(file, f, ensure_ascii=False)

    print(k, 'требуется в', round(v / sum_item * 100, 2), '%', 'найденных вакансий')
    print('Всего упоминаний:', v)
    print('Это', round(v / sum_all_skills * 100, 2), '%', 'среди всех ключевых навыков', '\n')
print('Средняя зарплата от:', average_salary)
