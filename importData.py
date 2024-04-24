import uuid

import pandas
from pymongo import MongoClient

df = pandas.read_csv("all_cities_weather_data.csv")
client = MongoClient("localhost", 27017)
client.drop_database("weather_data")
db = client.weather_data

# 城市编号名称,去重转字典
city_info = df[["citycode", "cityname"]].drop_duplicates().to_dict("records")

# 城市数据保存
db.cities.insert_many(city_info)

weathers = df.to_dict("records")

for item in weathers:

    item["_id"] = str(uuid.uuid4())
    db.weather.insert_one(item)

