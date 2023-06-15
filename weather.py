from cProfile import label
import csv
import chardet
import requests
from lxml import etree
from fake_useragent import UserAgent
import pandas as pd
from matplotlib import pyplot as plt

# 随机产生请求头，UserAgent用于生成随机的 UserAgent，可以在模拟请求时使用，增加爬虫的隐蔽性。
ua = UserAgent(verify_ssl=False, fallback=r"C:\Users\20138\Desktop\fake_useragent.json")


# 随机切换请求头。random_ua() 函数返回一个随机的 UserAgent，用于发送 HTTP 请求时设置请求头部。函数中先实例化了一个 UserAgent，然后使用它的 random 方法随机生成一个 UserAgent，并将其设置为请求头部中的 User-Agent 字段。
def random_ua():
    headers = {
        "user-agent": ua.random
    }
    return headers


# 选择城市，city_num() 函数用于查询城市的编号。
def city_num():
    # 提示用户输入城市名称
    city = input("请输入您想要查询天气情况的城市：")
    # 读取城市名称和编号的数据文件
    file = pd.read_csv('C:/Users/20138/Desktop/中国天气城市编号.csv', encoding="utf_8_sig")
    # 使用 Pandas 库查询城市名称是否在数据文件中
    index = file[file['城市'] == '{}'.format(city)].index.tolist()[
        0]  # 根据城市查找行标签
    num = file.loc[index, '编号']  # 根据行标签和列表签锁定值
    # 返回城市名称和编号
    return city, num


# 解析页面
# res_text(url) 函数用于发送 HTTP GET 请求，并将响应内容转化为 HTML 解析树对象。它使用了 requests 库发送了一个 GET 请求，设置了一个随机的 UserAgent 作为请求头部，并使用 chardet 自动检测响应的编码格式。然后，将响应内容转化为 HTML 树对象，并返回该对象。
def res_text(url):
    # 发送 HTTP GET 请求并获取响应，返回一个 Response 对象，其中包含了服务器返回的响应。
    res = requests.get(url=url, headers=random_ua())
    # 使用 chardet 自动检测响应的编码格式，chardet.detect(res.content) 方法可以自动检测响应的编码格式，并返回一个识别结果字典。
    res.encoding = chardet.detect(res.content)['encoding']
    # text 属性可以获取响应内容的 Unicode 字符串。
    response = res.text
    # etree.HTML() 方法来将 Unicode 字符串解析成 HTML 解析树对象。HTML 解析树对象可以用于 XPath 和 CSS Selector 提取 HTML 中的内容，包括标签和文本等。最后将解析后的 HTML 树对象作为函数的返回结果。
    html = etree.HTML(response)
    return html


# 获得未来七天及八到十五天的页面链接
def get_url(url):
    # 调用 res_text(url) 函数获取 URL 对应的 HTML 解析树对象
    html = res_text(url)
    # 使用 XPath 来查找包含未来七天和八到十五天天气数据页面链接的元素，将查找到的 URL 进行拼接，最后返回两个天气数据页面的 URL。
    url_7 = 'http://www.weather.com.cn/' + \
        html.xpath('//*[@id="someDayNav"]/li[2]/a/@href')[0]  # 获取未来七天数据的 URL
    url_8_15 = 'http://www.weather.com.cn/' + \
        html.xpath('//*[@id="someDayNav"]/li[3]/a/@href')[0]  # 获取8-15天数据的 URL
    return url_7, url_8_15


# 获取未来七天的天气情况
def get_data_7(url):
    # 调用 res_text(url) 函数获取对应 URL 对应的 HTML 解析树对象。
    html = res_text(url)
    # 使用 XPath 表达式从解析树对象中获取未来七天的天气数据，包括日期、天气情况、最低气温和最高气温。
    list_s = html.xpath('//*[@id="7d"]/ul/li')  # 获取天气数据列表
    Date, Weather, Low, High = [], [], [], []
    for i in range(len(list_s)):
        list_date = list_s[i].xpath('./h1/text()')[0]  # 获取日期
        list_weather = list_s[i].xpath('./p[1]/@title')[0]  # 获取天气情况
        tem_low = list_s[i].xpath('./p[2]/i/text()')  # 获取最低气温
        tem_high = list_s[i].xpath('./p[2]/span/text()')  # 获取最高气温
        if tem_high == []:  # 由于在白天最高气温和晚上最高气温是不同的，所以遇到夜晚情况，筛掉当天的最高气温
            tem_high = tem_low  # 无最高气温时，使最高气温等于最低气温
        # 将气温数据处理，需要将气温的字符串形式中的 “℃” 符号去掉，并将结果转换为整数类型。
        tem_low = int(tem_low[0].replace('℃', ''))
        tem_high = int(tem_high[0].replace('℃', ''))
        # 数据经过处理后，调用了对应的列表的 append() 方法，将将获取到的日期、天气情况、最低气温和最高气温依次添加到对应的列表 Date、Weather、Low 和 High 中。
        # 最终，这些列表中分别存储着未来七天的日期、天气情况、最低气温和最高气温的数据，便于后续整理成 Pandas 数据框。
        Date.append(list_date), Weather.append(
            list_weather), Low.append(tem_low), High.append(tem_high)
    excel = pd.DataFrame()  # 定义一个数据框将获取到的日期、天气情况、最低气温和最高气温分别存储到对应的列中，最后将该数据框作为函数的返回值。
    excel['日期'] = Date
    excel['天气'] = Weather
    excel['最低气温'] = Low
    excel['最高气温'] = High
    return excel


def get_data_8_15(url):
    html = res_text(url)
    # 使用 XPath 表达式从解析树对象中获取未来8-15天的天气数据，包括日期、天气情况、最低气温和最高气温。
    list_s = html.xpath('//*[@id="15d"]/ul/li')  # 获取天气数据列表
    Date, Weather, Low, High = [], [], [], []
    for i in range(len(list_s)):
        # 调用 list_s[i].xpath('./span/text()') 函数从解析树对象中获取该天气信息的日期、天气情况、最低气温和最高气温等信息（分别保存在 data_s 中）。注意，这里的 XPath 表达式 './span/text()' 是针对每一个 li 标签自身的路径，而不是基于整个文档的路径。
        # data_s[0]是日期，如：周二（11日），data_s[1]是天气情况，如：阴转晴，data_s[2]是最低温度，如：/-3℃
        data_s = list_s[i].xpath('./span/text()')
        # 获取日期情况，modify_str() 函数的作用是将 data_s[0] 中的日期字符串进行处理，去掉其中的空格和“周”字。
        date = modify_str(data_s[0])
        weather = data_s[1]  # 获取天气情况
        # 获取最低气温和最高气温数据进行处理，从字符串类型转化为整数类型，并存储到对应的变量low和 high 中。
        low = int(data_s[2].replace('/', '').replace('℃', ''))
        high = int(list_s[i].xpath('./span/em/text()')[0].replace('℃', ''))
        # 数据经过处理后，调用了对应的列表的 append() 方法，将将获取到的日期、天气情况、最低气温和最高气温依次添加到对应的列表 Date、Weather、Low 和 High 中。
        # 最终，这些列表中分别存储着未来8-15天的日期、天气情况、最低气温和最高气温的数据，便于后续整理成 Pandas 数据框。
        Date.append(date), Weather.append(
            weather), Low.append(low), High.append(high)
    excel = pd.DataFrame()  # 定义一个数据框将获取到的日期、天气情况、最低气温和最高气温分别存储到对应的列中，最后将该数据框作为函数的返回值。
    excel['日期'] = Date
    excel['天气'] = Weather
    excel['最低气温'] = Low
    excel['最高气温'] = High
    return excel


# 将8-15天日期格式改成与未来7天一致，将形如“周二（11日）”这样的日期字符串转换为“11日（周二）”的格式。
def modify_str(date):
    # split() 方法将日期字符串按照“（”分割，获取日期和星期的信息。
    date_1 = date.split('（')
    # 将日期信息和星期信息用“（”和“）”括起来
    date_2 = date_1[1].replace('）', '')
    date_result = date_2 + '（' + date_1[0] + '）'
    # 返回转换后的日期字符串。
    return date_result


# 实现数据可视化，根据这些参数绘制出对应城市未来 15 天的气温变化图。
def get_image(city, date, weather, high, low):
    # 用来正常显示中文字体，使得图表标题、坐标轴标签等中文显示正常。
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 图表中负号可以正常显示。
    plt.rcParams['axes.unicode_minus'] = False
    # 根据数据绘制图形，初始化一个绘图对象（Figure），设置图形的 dpi 值为 128，设置图形的大小为 (10, 6)。
    fig = plt.figure(dpi=128, figsize=(10, 6))
    # 添加子图，设置子图的位置为 “1×1” 的第 1 个位置。
    ax = fig.add_subplot(111)
    # plot() 方法绘制两条折线图，date 是横坐标（日期），high 、low是纵坐标（最高气温）分别表示最高气温和最低气温。其中，通过设置 alpha 参数为透明度设置为0.5，marker 参数为 ‘*’ 和 ‘o’ 使得每个数据点有不同的形状。
    plt.plot(date, high, c='red', alpha=0.5, marker='*')
    plt.plot(date, low, c='blue', alpha=0.5, marker='o')
    # fill_between()给图表中两条折线中间的部分上色，date 是横坐标，high 和 low 是纵坐标，用一个蓝色的半透明区域来填充两条曲线之间的空白处，透明度为0.2。
    plt.fill_between(date, high, low, facecolor='blue', alpha=0.2)
    # 使用 format() 函数来将城市名 city 嵌入到字符串中。字号为 24。
    plt.title('{}近15天天气预报'.format(city), fontsize=24)
    # 坐标轴的标签，分别为“日期”和“气温”，字号为 12。
    plt.xlabel('日期', fontsize=12)
    # 旋转 x 轴上的标签，避免标签重叠，使其看起来更加清晰
    fig.autofmt_xdate()
    plt.ylabel('气温', fontsize=12)
    # 参数刻度线设置，设置刻度线的参数，包括坐标轴、标尺和字号等信息。
    plt.tick_params(axis='both', which='major', labelsize=10)
    # 设置横坐标的刻度。由于 15 天的数据比较密集，这里只设置每个刻度之间的间隔为 1，以便能够清晰地查看横坐标的日期。
    plt.xticks(date[::1])
    # 给图表的每个数据点进行标注。循环遍历 15 天的天气数据，然后使用 annotate() 函数
    # 在对应位置标注天气情况、最高气温和最低气温等信息。
    for i in range(15):
        ax.annotate(weather[i], xy=(date[i], low[i]+1))
        ax.annotate(str(high[i])+'℃', xy=(date[i], high[i]+0.2))
        ax.annotate(str(low[i])+'℃', xy=(date[i], low[i]+0.2))
    # 绘制图片
    plt.show()


# 定义了一个字典，用来存储已注册的用户和对应的密码。
users = {
    'admin': '123'
}


def main():
    # 调用了 city_num() 函数获取用户输入的城市名称和对应的代号，并通过解包将其赋值给变量 city 和 num
    city, num = city_num()
    # 使用城市的代号 num 拼接出相应的 URL 地址，用于获取天气信息。
    base_url = 'http://www.weather.com.cn/weather1d/{}.shtml'.format(num)
    # 调用了 get_url() 函数并使用解包来获取函数返回的 url_7 和 url_8_15 两个变量，这两个变量分别表示获取未来7天天气信息和获取8-15天天气信息所需的 URL。
    url_7, url_8_15 = get_url(base_url)
    # 调用了 get_data_7() 和 get_data_8_15() 函数，并将它们返回的天气数据存储在 data_1 和 data_2 两个变量中。
    data_1 = get_data_7(url_7)
    data_2 = get_data_8_15(url_8_15)
    # 使用 pandas 库中的 concat() 函数将两个 DataFrame 拼接成一个，并忽略原来的索引，重新按行索引排序，得到一个新的 data 变量，其中包含了未来 15 天的天气数据。ignore_index=True实现两张表拼接，不保留原索引
    data = pd.concat([data_1, data_2], axis=0, ignore_index=True)
    # 获取用户输入的用户名和密码
    username = input("请输入用户名：")
    password = input("请输入密码：")
    # 检查用户名和密码是否正确，如果用户名和密码匹配成功，就调用 get_image() 函数生成该城市的气温数据可视化图表；否则提示用户名或密码错误。
    if username in users and users[username] == password:
        city = input("请再次确认您想要查询的城市：")
        get_image(city, data['日期'], data['天气'], data['最高气温'], data['最低气温'])
    else:
        print("用户名或密码错误，请重新登录！")


# 判断该模块是作为入口程序运行，还是被其他程序导入运行。如果是作为入口程序运行，就执行 main() 函数。
if __name__ == '__main__':
    main()
