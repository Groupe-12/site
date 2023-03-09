import gevent
from gevent.queue import Queue
from gevent import monkey

monkey.patch_all()
import requests, bs4, csv
from bs4 import BeautifulSoup


def data():
    global name, cals, i, cal_list, name_list
    url = 'https://www.les-calories.fr/'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    title = soup.title.text

    all_ali = []
    alis = soup.select('div.menus')
    for ali in alis:
        name_list = []
        cal_list = []
        elements = ali.select('div.description>b')[:10000]
        cals = ali.select('span.cost')[:10000]
        for element in elements:
            name_list.append(element.text.strip())
        name = ' '.join(name_list)
        for cal in cals:
            cal_list.append(cal.text.strip())
        cal = ' '.join(cal_list)

    for i in range(len(name_list)):
        all_ali.append({
            "Nom de l'aliment": name_list[i],
            'Calories': cal_list[i]
        })

    #print(all_ali)
    with open('food_calories.csv', 'w', newline='') as csvfile:
        fieldnames = ['Nom de l\'aliment', 'Calories']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for ali in all_ali:
            writer.writerow(ali)


data()
