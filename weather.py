from cProfile import label
import csv
import chardet
import requests
from lxml import etree
from fake_useragent import UserAgent
import pandas as pd
from matplotlib import pyplot as plt


# 随机产生请求头
ua = UserAgent(verify_ssl=False, fallback=r"C:\Users\20138\Documents\Tencent Files\2013876441\FileRecv\fake_useragent.json")


# 随机切换请求头
def random_ua():
    headers = {
        "user-agent": ua.random
    }
    return headers


# 选择城市

def city_num():
    city = input("请输入您想要查询天气情况的城市：")
    file = pd.read_csv('C:/Users/20138/Documents/Tencent Files/2013876441/FileRecv/中国天气城市编号.csv', encoding="utf_8_sig")
    index = file[file['城市'] == '{}'.format(city)].index.tolist()[
        0]  # 根据城市查找行标签
    num = file.loc[index, '编号']  # 根据行标签和列表签锁定值
    return city, num


# 解析页面
def res_text(url):
    res = requests.get(url=url, headers=random_ua())
    res.encoding = chardet.detect(res.content)['encoding']
    response = res.text
    html = etree.HTML(response)
    return html


# 获得未来七天及八到十五天的页面链接
def get_url(url):
    html = res_text(url)
    url_7 = 'http://www.weather.com.cn/' + \
        html.xpath('//*[@id="someDayNav"]/li[2]/a/@href')[0]
    url_8_15 = 'http://www.weather.com.cn/' + \
        html.xpath('//*[@id="someDayNav"]/li[3]/a/@href')[0]
    # print(url_7)
    # print(url_8_15)
    return url_7, url_8_15


# 获取未来七天的天气情况
def get_data_7(url):
    html = res_text(url)
    list_s = html.xpath('//*[@id="7d"]/ul/li')  # 获取天气数据列表
    Date, Weather, Low, High = [], [], [], []
    for i in range(len(list_s)):
        list_date = list_s[i].xpath('./h1/text()')[0]  # 获取日期，如：4日（明天）
        # print(list_data)
        list_weather = list_s[i].xpath('./p[1]/@title')[0]  # 获取天气情况，如：小雨转雨夹雪
        # print(list_weather)
        tem_low = list_s[i].xpath('./p[2]/i/text()')  # 获取最低气温
        tem_high = list_s[i].xpath('./p[2]/span/text()')  # 获取最高气温
        if tem_high == []:  # 遇到夜晚情况，筛掉当天的最高气温
            tem_high = tem_low  # 无最高气温时，使最高气温等于最低气温
        tem_low = int(tem_low[0].replace('℃', ''))  # 将气温数据处理
        tem_high = int(tem_high[0].replace('℃', ''))
        # print(type(tem_high))
        Date.append(list_date), Weather.append(
            list_weather), Low.append(tem_low), High.append(tem_high)
    excel = pd.DataFrame()  # 定义一个二维列表
    excel['日期'] = Date
    excel['天气'] = Weather
    excel['最低气温'] = Low
    excel['最高气温'] = High
    # print(excel)
    return excel


def get_data_8_15(url):
    html = res_text(url)
    list_s = html.xpath('//*[@id="15d"]/ul/li')
    Date, Weather, Low, High = [], [], [], []
    for i in range(len(list_s)):
        # data_s[0]是日期，如：周二（11日），data_s[1]是天气情况，如：阴转晴，data_s[2]是最低温度，如：/-3℃
        data_s = list_s[i].xpath('./span/text()')
        # print(data_s)
        date = modify_str(data_s[0])  # 获取日期情况
        weather = data_s[1]
        low = int(data_s[2].replace('/', '').replace('℃', ''))
        high = int(list_s[i].xpath('./span/em/text()')[0].replace('℃', ''))
        # print(date, weather, low, high)
        Date.append(date), Weather.append(
            weather), Low.append(low), High.append(high)
    # print(Date, Weather, Low, High)
    excel = pd.DataFrame()  # 定义一个二维列表
    excel['日期'] = Date
    excel['天气'] = Weather
    excel['最低气温'] = Low
    excel['最高气温'] = High
    # print(excel)
    return excel


# 将8-15天日期格式改成与未来7天一致
def modify_str(date):
    date_1 = date.split('（')
    date_2 = date_1[1].replace('）', '')
    date_result = date_2 + '（' + date_1[0] + '）'
    return date_result


# 实现数据可视化
def get_image(city, date, weather, high, low):
    # 用来正常显示中文标签
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 用来正常显示负号
    plt.rcParams['axes.unicode_minus'] = False
    # 根据数据绘制图形
    fig = plt.figure(dpi=128, figsize=(10, 6))
    ax = fig.add_subplot(111)
    plt.plot(date, high, c='red', alpha=0.5, marker='*')
    plt.plot(date, low, c='blue', alpha=0.5, marker='o')
    # 给图表中两条折线中间的部分上色
    plt.fill_between(date, high, low, facecolor='blue', alpha=0.2)
    # 设置图表格式
    plt.title('{}近15天天气预报'.format(city), fontsize=24)
    plt.xlabel('日期', fontsize=12)
    # 绘制斜的标签，以免重叠
    fig.autofmt_xdate()
    plt.ylabel('气温', fontsize=12)
    # 参数刻度线设置
    plt.tick_params(axis='both', which='major', labelsize=10)
    # 修改刻度
    plt.xticks(date[::1])
    # 对点进行标注，在最高气温点处标注当天的天气情况
    for i in range(15):
        ax.annotate(weather[i], xy=(date[i], low[i]+1))
        ax.annotate(str(high[i])+'℃', xy=(date[i], high[i]+0.2))
        ax.annotate(str(low[i])+'℃', xy=(date[i], low[i]+0.2))
    # 显示图片
    plt.show()


users = {
    'admin': '123'
}


def main():
    city, num = city_num()
    base_url = 'http://www.weather.com.cn/weather1d/{}.shtml'.format(num)
    url_7, url_8_15 = get_url(base_url)
    data_1 = get_data_7(url_7)
    data_2 = get_data_8_15(url_8_15)
    # ignore_index=True实现两张表拼接，不保留原索引
    data = pd.concat([data_1, data_2], axis=0, ignore_index=True)
    # get_image(city, data['日期'], data['天气'], data['最高气温'], data['最低气温'])
    # 获取用户输入的用户名和密码
    username = input("请输入用户名：")
    password = input("请输入密码：")
    # 检查用户名和密码是否正确
    if username in users and users[username] == password:
        city = input("请再次确认您想要查询的城市：")
        get_image(city, data['日期'], data['天气'], data['最高气温'], data['最低气温'])

    else:

        print("用户名或密码错误，请重新登录！")


if __name__ == '__main__':
    main()
