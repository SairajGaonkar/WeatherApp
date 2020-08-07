import requests
import bs4
import collections
from zipcodes import range_key_dict
import pandas as pd
from datetime import datetime
import os
from os import path
import matplotlib.pyplot as plt
import sys

WeatherReport = collections.namedtuple('WeatherReport','cond, temp, scale, loc,pres,humid')

def main():
    print_the_header()
    code = input("Enter Zip code for the weather info you want (47401): ")
    code = code.lstrip('0')
    if range_key_dict.get(int(code)) is None:
        print("Not a valid zipcode.")
        exit(1)
    html = scrap_web(int(code))
    report = get_weather_details(html)
    print("The temp of  {2} is: {0} {1} \nThe condition is: {3} \nThe pressure is: {4} in. \nThe humidiy is: {5} %".format(
          report.temp,
          report.scale,
          report.loc,
          report.cond,
          report.pres,
          report.humid
          ))
    record_in_file(report.loc,report.temp,code)

def record_in_file(loc,temp,code):
    x = datetime.now()
    date = str(x.month)+'/'+str(x.day)+'/'+str(x.year)
    record = {
        'Date': date,
        'PinCode': code,
        'Location': loc,
        'Temperature': temp
    }
    b = True
    file_exists = path.exists("WeatherReport.csv")
    if file_exists:
        b = False
    df = pd.DataFrame(record, columns= ['Date','PinCode','Location','Temperature'], index = [0])
    relativePath=os.getcwd()
    dataFilePath=relativePath+"\\WeatherReport.csv"
    df.to_csv (dataFilePath, index = False, header=b, mode='a')
    plot_from_file(code)

def plot_from_file(code):
    relativePath=os.getcwd()
    dataFilePath=relativePath+"\\WeatherReport.csv"
    data = pd.read_csv(dataFilePath)
    data = data.loc[(data.PinCode == int(code))]
    data.sort_values("Date", inplace = True)
    data.drop_duplicates(subset ="Date", keep = 'first', inplace = True)
    data = data.tail(10)
    cols = []
    for row in data:
        cols.append(row)
    p = data.plot(x = cols[0], y = cols[3], figsize= (10,10),kind='line')
    plt.show()

def print_the_header():
    print('--------------------------------------------------')
    print('                   Weather App                    ')
    print('--------------------------------------------------')
    print()


def scrap_web(zipcode):
    pin = str(zipcode)
    if len(pin) < 5:
        pin ='0'+ pin
    default_url = 'https://www.wunderground.com/weather/us/'
    url = default_url+range_key_dict.get(zipcode)+pin
    response = requests.get(url)
    return response.text


def get_weather_details(html):
    soup = bs4.BeautifulSoup(html, 'html.parser')
    loc = soup.find(class_='region-content-top').find('h1').get_text()
    condition = soup.find(class_='condition-icon').get_text()
    temp = soup.find(class_='wu-unit-temperature').find(class_='wu-value').get_text()
    scale = soup.find(class_='wu-unit-temperature').find(class_='wu-label').get_text()
    pressure = soup.find(class_='test-false wu-unit wu-unit-pressure ng-star-inserted').find(class_='wu-value wu-value-to').get_text()
    humidity = soup.find(class_='test-false wu-unit wu-unit-humidity ng-star-inserted').find(class_='wu-value wu-value-to').get_text()
    loc = clean_data(loc)
    loc = filter_location(loc)
    condition = clean_data(condition)
    temp = clean_data(temp)
    scale = clean_data(scale)
    pressure = clean_data(pressure)
    humidity = clean_data(humidity)
    report = WeatherReport(cond=condition, temp=temp, scale=scale, loc=loc,pres=pressure,humid=humidity)
    return report


def filter_location(loc: str):
    parts = loc.split(' ')
    parts = parts[:len(parts)-2]
    location = ""
    for p in parts:
        location += p
    print(location)
    return location


def clean_data(text: str):
    if not text:
        return text
    text = text.strip()
    return text


if __name__ == '__main__':
    main()