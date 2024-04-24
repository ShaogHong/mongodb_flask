import json

from flask import Flask, render_template, request
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.results import DeleteResult

app = Flask(__name__, static_folder="static")

client = MongoClient("localhost", 27017)
db: Database = client.weather_data


# 事先准备两个方法,查询数据
def get_city_info(name):
    """
从数据库中检索有关城市的信息。

参数：
    name （str）：要检索其信息的城市的名称。

返回：
    dict：如果找到有关城市的信息，否则无。
    """
    city = db.cities.find_one({"cityname": name})
    if city is None:
        return None

    # 在返回城市信息之前删除“_id”字段
    city.pop("_id")
    return city


def get_weather_by_city(citycode):
    """
检索给定城市代码的天气数据。

args：
        citycode （str）：要检索其天气数据的城市代码。

返回：
        list：给定城市代码的天气数据列表。
    """
    # 在数据库中查询给定城市代码的天气数据
    result = db.weather.find({"citycode": citycode}).sort("updatetime", 1)

    # 将结果转换为词典列表
    data = [row for row in result]

    # 返回天气数据列表
    return data


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/edit/<id>")
def edit(id):
    info = db.weather.find_one({"_id": id})

    return render_template("edit.html", data=info)


@app.route("/weather/save", methods=["POST"])
def save():
    """
    处理 POST 请求以更新数据库中的天气数据。
    """
    data = request.form.to_dict()

    # 检索和删除旧数据
    old = db.weather.find_one_and_delete({"_id": data["_id"]})

    # 使用新值更新旧数据
    old["fleelst"] = data["fleelst"]
    old["winddirect"] = data["winddirect"]
    old["windpower"] = data["windpower"]
    old["humidity"] = data["humidity"]
    old["temperature"] = data["temperature"]
    old["rain"] = data["rain"]
    old["airpressure"] = data["airpressure"]
    old["updatetime"] = data["updatetime"]

    # 将更新的数据保存回数据库
    result = db.weather.insert_one(old)

    # 根据插入状态返回成功消息
    return {"success": True} if result.inserted_id else {"success": False}


@app.route("/weather/<cityname>")
def getWeatherByCityName(cityname):
    """
   检索给定城市名称的天气数据。

参数：
        cityname （str）：城市的名称。

返回：
        str：包含城市天气数据的 JSON 字符串。"""

    # 根据城市名称检索城市信息
    city = get_city_info(cityname)

    if city is not None:
        # 如果城市数据存在，请检索城市的天气数据
        weather_data = get_weather_by_city(city["citycode"])

        # 将数据转换为 JSON 字符串并返回
        return json.dumps({"code": 200, "data": weather_data})
    else:
        # 如果城市数据不存在，则返回错误消息
        return json.dumps({"msg": "没有该城市数据", "code": 201})


@app.route("/weather/delete/<id>")
def deleteWeatherById(id):
    result: DeleteResult = db.weather.delete_one({"_id": id})
    if result.deleted_count == 1:
        return {"msg": "删除成功", "code": 200}
    else:
        return {"msg": "删除失败", "code": 201}


if __name__ == '__main__':
    app.run(debug=True)
