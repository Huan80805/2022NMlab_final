from bs4 import BeautifulSoup
import requests
from datetime import datetime

def month_to_chi(date):
    D_mon_to_chi = {0:'', 1:'一', 2:'二', 3:'三', 4:'四', 5:'五', 6:'六'
                    , 7:'七', 8:'八', 9:'九', 10:'十', 11:'十一', 12:'十二'}
    D_day_to_chi0 = {1:'十', 2:'二十', 3:'三十'}
    D_day_to_chi1 = {0:'', 1:'一', 2:'二', 3:'三', 4:'四', 5:'五', 6:'六', 7:'七', 8:'八', 9:'九'}
    month = date.split('/')[0]
    day = date.split('/')[1]
    
    result = ''
    
    result += D_mon_to_chi[int(month)]
    result += '月'
    
    if len(day) == 2:
        result += D_day_to_chi0[int(day[0])]
        result += D_day_to_chi1[int(day[1])]
        result += '日'
    if len(day) == 1:
        result += D_day_to_chi1[int(day[0])]
        result += '日'
        
    return result

def temp_number_to_chinese(temp_number):
    D_num_to_chi = {0:'', 1:'一', 2:'二', 3:'三', 4:'四', 5:'五', 6:'六', 7:'七', 8:'八', 9:'九'}
    result = ''
    if len(temp_number.split('~')[0]) == 2:
        if temp_number[0] == '1':
            result += '十'
        if temp_number[0] == '2':
            result += '二十'
        if temp_number[0] == '3':
            result += '三十'
        result += D_num_to_chi[int(temp_number[1])]
        result += '至'
    if len(temp_number.split('~')[0]) == 1:
        result += D_num_to_chi[int(temp_number[0])]
        result += '至'
    if len(temp_number.split('~')[1]) == 2:
        if temp_number.split('~')[1][0] == '1':
            result += '十'
        if temp_number.split('~')[1][0] == '2':
            result += '二十'
        if temp_number.split('~')[1][0] == '3':
            result += '三十'
        result += D_num_to_chi[int(temp_number.split('~')[1][1])]
    if len(temp_number.split('~')[1]) == 1:
        result += D_num_to_chi[int(temp_number[0])]
    return result + '度'

def get_weather(location):
    response = requests.get('https://weather.sina.com.tw/tw_week.shtml')
    soup = BeautifulSoup(response.text, "html.parser")
    
    # date
    date = str(int(datetime.now().strftime("%Y/%m/%d").split('/')[1]))
    date += '/'
    date += str(int(datetime.now().strftime("%Y/%m/%d").split('/')[2]))
    # N M S EN
    '''
    N_rain, M_rain, S_rain, EN_rain = [], [], [], []
    N_temp, M_temp, S_temp, EN_temp = [], [], [], []
    
    for elem in soup.find_all('tr')[5].find_all('td')[1:]:
        N_rain.append(elem.img['alt'])
    for elem in soup.find_all('tr')[5].find_all('em'):
        N_temp.append(elem.string)
    
    for elem in soup.find_all('tr')[6].find_all('td')[1:]:
        M_rain.append(elem.img['alt'])
    for elem in soup.find_all('tr')[6].find_all('em'):
        M_temp.append(elem.string)
        
    for elem in soup.find_all('tr')[7].find_all('td')[1:]:
        S_rain.append(elem.img['alt'])
    for elem in soup.find_all('tr')[7].find_all('em'):
        S_temp.append(elem.string)
        
    for elem in soup.find_all('tr')[8].find_all('td')[1:]:
        EN_rain.append(elem.img['alt'])
    for elem in soup.find_all('tr')[8].find_all('em'):
        EN_temp.append(elem.string)
    '''
    result = f'{location}，{month_to_chi(date)}的天氣為'
    
    N = soup.find_all('tr')[5].find_all('td')[1].img['alt']
    M = soup.find_all('tr')[6].find_all('td')[1].img['alt']
    S = soup.find_all('tr')[7].find_all('td')[1].img['alt']
    EN = soup.find_all('tr')[8].find_all('td')[1].img['alt']
    
    N_temp = soup.find_all('tr')[5].find_all('td')[1].find('em').string[:-2]
    M_temp = soup.find_all('tr')[6].find_all('td')[1].find('em').string[:-2]
    S_temp = soup.find_all('tr')[7].find_all('td')[1].find('em').string[:-2]
    EN_temp = soup.find_all('tr')[8].find_all('td')[1].find('em').string[:-2]
    
    result += N
    result += f'，溫度為'
    result += temp_number_to_chinese(N_temp)
    
    return result

def search_weather(search_city):
    response = requests.get('https://weather.sina.com.tw/tw_today.shtml')
    soup = BeautifulSoup(response.text, "html.parser")
    # date
    date = str(int(datetime.now().strftime("%Y/%m/%d").split('/')[1]))
    date += '/'
    date += str(int(datetime.now().strftime("%Y/%m/%d").split('/')[2]))
    # city
    city = []
    for elem in soup.find_all('td', class_='txta'):
        city.append(elem.string)
    # weather
    weather = []
    for elem in soup.find_all('td', class_='txtb'):
        weather.append(elem.text)
    # temp
    temp = []
    for elem in soup.find_all('td', class_='txtc'):
        temp.append(elem.string[:-2])
    # prob
    prob = []
    for elem in soup.find_all('td', class_=''):
        prob.append(elem.string)

    i = city.index(search_city)
    result = f'{city[i]}，{month_to_chi(date)}的天氣為攝氏{weather[i]}，氣溫為{temp_number_to_chinese(temp[i])}，降雨機率為{prob[i]}'

    return result


if __name__ == '__main__':   
    r = search_weather('南投縣')

    print(r)