import requests
from bs4 import BeautifulSoup
import pickle
import os
import time
from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
import os

basedir = os.path.abspath(os.path.dirname(__file__))
*将变量 basedir 设为当前 Python 文件所在目录的绝对路径。*

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'db.sqlite'),
    SECRET_KEY='secret_key'
)

db = SQLAlchemy(app)
from models import *

PATH = "./static/splider_file"
PATH_PKL = "PKL"
PATH_PIC = "PIC"


def write_pkl(path, name, data):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, name), "wb") as f:
        f.write(pickle.dumps(data))


def read_pkl(path, name, default={}):
    fpath = os.path.join(path, name)
    if not os.path.isfile(fpath):
        return default
    try:
        with open(fpath, "rb") as f:
            return pickle.loads(f.read())
    except Exception:
        return default


headers = {
    "cookie": "gtmEnvironnement=Web; lark-consent=0; lark-consentId=a73570db-5c3a-4148-9d98-83372c88a590; lark-browser-uuid=f70cae7f-fd5c-41bd-b148-bd70b79d36dc; lark-cart=98af28d3-34e3-437a-94de-66a757bbef0c; OptanonAlertBoxClosed=2023-03-25T11:54:02.695Z; lark-ab=1; _gcl_au=1.1.458542118.1679745264; valiuz-id=1526058b-412a-4c41-865a-a051d293faf4; _scid=aecd3f2f-da3d-4608-89ac-d15aa3e818b7; _cs_c=1; htk_auchan_fr_visit=82emby1w8orft; mics_vid=34190333965; mics_lts=1679745314127; htk_auchan_fr_first_visits=1010000000; lark-journey=47b9fd46-bb95-4584-9f1b-0f9031796727; connect.sid=s%3AZUkMFslAek0I04e9XMHBFatLnCusgz1v.sMmY61V4Hk4V96daIEEed5vR2JFPxi0HsGkHxQIiopo; lark-session=7efc30c7-22b3-48a9-8a72-98e96aef0181+1680709099259; eupubconsent-v2=CPpKdoAPpKdoAAcABBENC-CsAP_AAAAAAChQJTwFwAIABbAZMAzQBsADiAHVgPLgesB9kD7gPvgfiB-kD9wQQggkCCcEFQQdgg-CFEEKgRogjUCOsEdwR8gj8CQ8EiQSQgkoCTUEnAShglICU4AAAAAA.f_gAAAAAAAAA; lark-history=true; kameleoonVisitorCode=_js_azebu6zkc4i3gdw0; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Apr+06+2023+00%3A37%3A54+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=6.33.0&isIABGlobal=false&consentId=f46bbcdd-775d-410a-817c-d7c6c85e8999&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CBG17%3A1&hosts=H41%3A1%2CH35%3A1%2CH47%3A1%2CH48%3A1%2CH34%3A1%2CH39%3A1%2CH66%3A1%2CH70%3A1%2CH71%3A1%2CH72%3A1%2CH73%3A1%2CH36%3A1%2CH11%3A1%2CH77%3A1%2CH78%3A1%2CH79%3A1%2CH80%3A1%2CH20%3A1%2CH82%3A1%2CH83%3A1%2CH84%3A1%2CH85%3A1%2CH91%3A1%2CH92%3A1%2CH57%3A1%2CH28%3A1%2CH95%3A1%2CH96%3A1%2CH98%3A1%2CH101%3A1%2CH102%3A1&genVendors=V20%3A1%2CV13%3A1%2CV32%3A1%2CV8%3A1%2CV7%3A1%2CV29%3A0%2CV6%3A1%2CV30%3A1%2CV14%3A1%2CV28%3A1%2CV31%3A1%2CV26%3A1%2CV11%3A1%2CV10%3A1%2CV18%3A1%2CV15%3A1%2CV21%3A1%2CV5%3A1%2CV4%3A1%2CV17%3A1%2CV23%3A1%2C&geolocation=CN%3BBJ&AwaitingReconsent=false; _cs_cvars=%7B%221%22%3A%5B%22authenticated%22%2C%22not_authenticated%22%5D%2C%223%22%3A%5B%22pageType%22%2C%22product%22%5D%2C%224%22%3A%5B%22pageSubType%22%2C%22PRODUCT%22%5D%2C%228%22%3A%5B%22sellerID%22%2C%22false%22%5D%2C%229%22%3A%5B%22sellerName%22%2C%22false%22%5D%2C%2210%22%3A%5B%22storeReference%22%2C%22false%22%5D%2C%2211%22%3A%5B%22sellerType%22%2C%22false%22%5D%2C%2219%22%3A%5B%22journeyType%22%2C%22GROCERY%22%5D%7D; _cs_id=80ea5c80-d5de-ad00-ee3c-532995470ac6.1679745264.2.1680712739.1680709134.1.1713909264911; _cs_s=8.0.0.1680714539150; _uetsid=f84e3660d3c711ed985ec50dbc4a4ef0; _uetvid=c9761600cb0311ed919e9fc86dd644c3; _scid_r=aecd3f2f-da3d-4608-89ac-d15aa3e818b7; cto_bundle=jIrtJF9jeWxYSTg5VDh1YjlDV1hLNm9VbVBTVGE5YVdqJTJCWkpLMTdKbTdJWTI4OFVHUVNzSHNNRU5GeXRXWSUyRjhodVkwbndNd1B5NU5kRmNIZUNpd3dLRUxDT0w0MGNPeENEbnFMQU02YTdNUzFCd2RjRUZWcTJoWnJrdzRIZEpyck9UJTJCUnZWakUySHVVR0VGQW9nYkxoJTJGcTh2USUzRCUzRA",
}


def test():
    base_url = "https://www.auchan.fr"
    url = f"{base_url}/fruits-legumes/legumes/carottes-poireaux-choux-navets/ca-n03021814"
    txt = requests.get(url, headers=headers)
    soup = BeautifulSoup(txt.content)
    for article in soup.find_all("article", class_="product-thumbnail"):
        _a = article.find("a", class_="product-thumbnail__details-wrapper")
        _href = _a.get("href") #获取食物链接

        tmp_url = f"{base_url}{_href}"
        print(tmp_url)
        try:
            res = desc(tmp_url)
            name = res["name"]
            FoodModels.query.filter_by(name=name).delete()#获取食物信息，如果有就进行删除

            obj = FoodModels(
                **res
            )#解析字典
            db.session.add(obj)
            db.session.commit()
        except Exception as e:
            print("E: ", e)


def desc(url):
    # url = f"https://www.auchan.fr/chou-blanc/pr-C1350282"
    txt = requests.get(url, headers=headers)
    soup = BeautifulSoup(txt.content)
    price = soup.find('div', class_='product-price--large').text
    price_single = soup.find('div', class_='product-price--small').text
    desc = soup.find("div", class_="product-description__content-wrapper").text
    pic_url = soup.find("div", class_="product-zoom__item").find("img").get("src")
    val_desc = soup.find("span", class_="product-description__feature-value").text
    title = soup.find("h1", class_="site-breadcrumb__title").text

    path = os.path.join(PATH, PATH_PIC)
    os.makedirs(path, exist_ok=True)#创建路径，保存信息
    name = time.time()
    name = f"{name}.jpg"
    with open(os.path.join(path, name), "wb") as f:#wb=写入二进制
        f.write(requests.get(pic_url).content)
    return {
        "pic": name,
        "name": str(title).strip(),
        "price": price_single,
        "desc": desc,
        "comm": val_desc,
    }


if __name__ == "__main__":
    test()
    # desc()
