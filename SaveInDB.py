import pymongo
import random
import datetime as dt
import googleapiclient
from apiclient.discovery import build
import re, requests, json, nltk
from textblob import TextBlob

myclient = pymongo.MongoClient(
    "mongodb+srv://infy:infy123@cluster0-kfqgc.mongodb.net/digital_signage?retryWrites=true&w=majority")
mydb = myclient["digital_signage"]
mycol = mydb["ads"]

file_server = 'https://localhost:8000'

rain_pics = '/rain/'
clear_pics = '/clear/'
sunny_pics = '/sunny/'


def findWeather(zip_code):
    import requests, json
    try:
        complete_url = 'http://api.openweathermap.org/data/2.5/forecast?id=524901&APPID=d0a277f376584b93674d757c6caf4841&zip={},in'.format(
            zip_code)

        response = requests.get(complete_url)

        x = response.json()

        if x["cod"] != "404":

            y = x['list'][0]['weather'][0]['main']
            return y
        else:
            print(" City Not Found ")
            return None
    except Exception as e:
        print(e)


def saveData(path, zipCode, adCategory, textContent, location):
    set = {"ad_path": path, "zipcode": zipCode, "ad_type": adCategory, "text_content": textContent,
           "location": location}
    mycol.insert_one(set)
    print("saved")


def fetchData(group_name):
    list_of_ads = []
    if group_name == "location":
        group_by = mycol.aggregate([{
            "$group": {
                "_id": "$location"
            }
        }])
        for x in group_by:
            group_by_list = list(mycol.find({"location": x['_id']}))
            for ad in group_by_list:
                ad["weather"] = findWeather(ad["zipcode"])
                list_of_ads.append(ad)

    elif group_name == "type":
        group_by = mycol.aggregate([{
            "$group": {
                "_id": "$ad_type"
            }
        }])
        for x in group_by:
            group_by_list = list(mycol.find({"ad_type": x['_id']}))
            for ad in group_by_list:
                ad["weather"] = findWeather(ad["zipcode"])
                del ad['_id']
                list_of_ads.append(ad)
    else:
        return "please enter the correct field"

    return list_of_ads


def random_ad(ads):
    text_list = []
    img_list = []
    for ad in ads:
        if ad['ad_type'] == 'string':
            text_list.append(ad)
        elif ad['ad_type'] == 'image':
            img_list.append(ad)

    if len(img_list) > 0:
        random_img = random.choice(img_list)
        text_content = random_img['text_content']
        if text_content is None:
            text_content = 'thumbs up taste the thunder'
        img_url = random_img['ad_path']

    elif len(text_list) > 0:
        random_txt = random.choice(text_list)
        text_content = random_txt['text_content']
        if text_content is None:
            text_content = 'thumbs up taste the thunder'
    else:
        text_content = 'ParleG'



    video = youtube_link(text_content)

    final = {'img_url':img_url, 'text_content': text_content, 'video':video}

    return json.dumps(final)


def weather_category(zip_code):
    mausam = findWeather(zip_code)
    ads = list(mycol.find({'zipcode': zip_code}))
    if mausam in ['Thunderstorm', 'Drizzle', 'Rain', 'Clouds', 'Snow']:
        category = 'rainy'
    elif mausam == 'clear' and ((dt.datetime().now().time() >= dt.time(9)) and (dt.datetime().now().time() >= dt.time(18))):  # 9-6
        category = 'sunny'
    else:
        category = 'clear'


    return random_ad(ads)



try:
    def youtube_link(text):
        # nltk.download('punkt')
        # nltk.download('brown')
        blob = TextBlob(text)
        blob = blob.correct()
        data = blob.noun_phrases
        if len(data) > 2:
            data = data[0:2]
        final_data = ' '.join(data)
        final_data = final_data + ' ads'
        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY = "AIzaSyBzMXePBfw0sb7J4P4xPwkVVIQoVCXVqEc"
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=DEVELOPER_KEY)

        request = youtube.search().list(
            part='snippet',
            q=final_data
        )
        response = request.execute()

        video_id = response['items'][0]['id']['videoId']
        thumbnail = response['items'][0]['snippet']['thumbnails']['high']['url']
        video_url = 'https://www.youtube.com/watch?v={}'.format(video_id)
        output = {'video_url': video_url, 'thumbnail': thumbnail}
        return output
except Exception as e:
    print(e)