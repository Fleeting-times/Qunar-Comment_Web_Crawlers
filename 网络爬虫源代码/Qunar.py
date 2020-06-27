import requests
import json
import re
from concurrent.futures import ThreadPoolExecutor

def write_json(hotels_dict, name):
    json_Data = json.dumps(hotels_dict, indent=4, ensure_ascii=False)

    filename = '{}.json'.format(name)
    with open(filename, 'a', encoding='utf8')as f:
        f.write(json_Data)



def get_comment_link(comment_page, ID):
    #comment_page为当前酒店的评论页数
    #ID为当前酒店ID

    #定义一个字典，用于存储当前酒店的评论及其对应的时间
    Comment_dict = {}

    for i in range(comment_page):
        #构建评论接口的URL
        url = 'https://hotel.qunar.com/napi/ugcCmtList?hotelSeq=sanya_{}&page={}&onlyGuru=false&rate=all&sort=hot'.format(ID, i+1)

        #设置请求头
        headers = {
            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'referer' : 'https://hotel.qunar.com/cn/sanya/dt-14850?fromDate=2020-04-03&toDate=2020-04-30&highQuality=true',
            'cookie' : 'QN99=9149; QN1=eIQjml3TdwCQ3F2E/eGkAg==; QunarGlobal=10.86.213.150_5cfe31_16e8204577e_-3faf|1574139648925; _i=RBTKSNoofqwxkwKR6kVV2LZonQix; QN601=5b95fb1cad13f2ba85cb58e44f734cc7; QN48=69694751-b8b2-49a8-a2e5-cc139c4788eb; fid=fce2e90b-98b3-46a8-bfd6-c6aec371ed44; ls=%u4E09%u4E9A; QN235=2020-01-04; _RF1=221.182.236.68; _RSG=nVaqD6dYLKEv9CaZYXeC5A; _RDG=288a553fa479172dd4313042afba770c5e; _RGUID=e5158a71-8dd2-47f1-a14c-a218a390c279; __utmz=183398822.1578467420.7.7.utmcsr=hotel.qunar.com|utmccn=(referral)|utmcmd=referral|utmcct=/; Qs_lvt_55613=1578205121%2C1578237557%2C1578272053%2C1578314717%2C1578498829; Hm_lvt_8fa710fe238aadb83847578e333d4309=1576498705,1578143378,1578205122,1578498830; Qs_pv_55613=3930803083783042600%2C4037954834071853600%2C297172186538473200%2C157535779686491170%2C2689651625665552400; __utma=183398822.809776704.1578272055.1578467420.1578537643.8; QN57=15785575104240.33633514162768785; QN58=1578566582448%7C1578566844006%7C2; _jzqa=1.3021954660394055700.1574150419.1578537643.1578580072.23; _jzqx=1.1574150419.1578580072.6.jzqsr=hotel%2Equnar%2Ecom|jzqct=/.jzqsr=hotel%2Equnar%2Ecom|jzqct=/; QN73=3753-3762; _qzja=1.10014274.1574150418799.1578537643381.1578580072225.1578580542100.1578580688845..0.0.64.20; QN300=s%3Dbaidu; QN205=s%3Dbaidu; QN277=s%3Dbaidu; csrfToken=3oJn1EV2qx7c8TzvzR6NJFSJphekWIZP; QN163=0; QN269=71B88350308611EAAB12FA163E08FC6A; HN1=v1aee9abe6905b3408520c2950f25c8619; HN2=qnkrgqzulzsnc; cityUrl=sanya; cityName=%25E4%25B8%2589%25E4%25BA%259A; checkInDate=2020-04-03; checkOutDate=2020-04-30; _vi=MjG4DbfgWl8kxl-R1kEnhvjqfGNxW053iP8DSsyTlds5nNDhDqp9xjXYiDcMwmL2lgWb1qcNc6Q1KtlC2EoX-AMopSUYxqDKG8FXYBfOTQMyZXdoyVJv9axMQht4zVMmfk2w0KFlQEaIXRJ12v8FrE1xZKWNEnXmlWlpLAg_9KL9; QN271=9078f373-ad3f-48b0-8e58-be55dacda40f; __qt=v1%7CVTJGc2RHVmtYMTh0TTQ4dWJSS25vaVVzUnNuVnF5L2t2KytiVkdscjNseWhLOTVNMmVlc0k1WnpGaE1xUXFRZHNQdDNCLzNZYWkrbDlWK0RnRFdnVEFpdEhCbXR6RU5pU0MwSDBkR3d6blZUOTMwajlmSHdsQU9zZVNYRFAvMnNGRTZ4UE94OXVNSGhTa09XY285NmVPOFNyR2FZZGFBcm1lVE1ZM3BmY0o0PQ%3D%3D%7C1585905910120%7CVTJGc2RHVmtYMSt6M0twWDFQRFJVcFFNczI0aDhMeFpoYXJBaW9EUkVIZlV5ZktrVWpkN1Fla1F3OWwxa2wxSEZQaitYNDN6L3NvcENtanhieS82OUE9PQ%3D%3D%7CVTJGc2RHVmtYMTgyNEpDcFlicTNFR3U5dFU3c2pTdS95Q3V5cDA3b3crajA5a0N0VmFFZGkzSmU2bkRxYUppMGxsdWdFZDFqQkwvM2xzMTlkK0U3VUxiVGN1OVExaXFuczlnMmdCNGxLN3lDRFlWbU41cGpVN3g2YzhRUXVqaENiUEEyelQ1eGxKQ0YwelViTkd5Zy92cmIxL1FMcVpMbWZlT2NKZWRyYmp2ZS83a0NsU3dTRTRBSGJhVEdraFJhbFFwTGhMRjVJWitRSVprczRJWXlsQmdhbXJLVVZpSTh4aWpPcEYzUHY3QURBeFlsYklOL0RJRGhEOFVVckU2UGxpa2N4WVFiempNcXJyVXRLclF1UUNLSjUyK2FlN3V0ZUNjVXllUVhTd3I1UWhCVUVCY3BiWnIyR2VLbjFwbHVEZ0hTejBGUEJ0VE5HSDIxaWkvL1Y2QzhPSVN3NXBnWXZFNmgwQnd1RFZadXAvcG9jUjBoeE5mc0srcmtJYlJRVk9Ja1Rzc1ZwdzVicUp2RjJYTnQvVFB6NHJCb1hpNFdVYkFYSDhLRHBtQllpcEZaTTIvNDkwVEh1Z3MrNllSVHFTWjdQM0JrZk5waVhvNHR6TjcrVnZWSE9VVTYvaGFVdThEZVJSV3hQbzFqdVNWL2VPZ2pLZStmM2k5d2d5QjRybGplQlYwWmIxemIrQzVBOFpVRklXV1dqQjEwMU5SZHVYZ2Vzc2lTeEZ2S2syRkZSS3Y3d0NBVWNDU0t6TExhdmpjbXJrNkFYWk9lcDAvemxnYWhpVEM4YnBlQnBsUnhZSzFSS3IvdklidGMrKy9Fb3BQZFR4RG1wenoxSXNYTkNPMXZmY29vdDVpT01XbTIwVWJ2K0d0anEyT09HWjIyUnRwcU42WjhXR0k9; QN267=86445296436490217'
        }
        html = requests.get(url, headers = headers)
        html.encoding = 'utf8'
        json_decoder = html.text

        #将不规则的JSON数据标准化
        start = json_decoder.find('{"ret":true,"errcode":0,"data":')
        end = json_decoder.find('}]}}') + len('}]}}')
        result = json.loads(json_decoder[start: end])

        # 用于判断当前循环正常运行的提示语句
        print('一共有{}页评论，当前正在提取第{}页评论'.format(comment_page, i))

        #开始迭代酒店当前翻页的每一条评论
        for r in result['data']['list']:

            # 暂时存储用户评论及评论时间的字典
            Comment = {}

            # 用户ID
            User_ID = r['uid']

            # 用户评论时间
            Comment['Cumment_time'] = re.findall(r'"modtime":"(.*?)","', r['content'])[0]

            # 用户评论
            Comment['User_comment'] = re.findall(r'feedContent":"(.*?)",', r['content'])[0].replace('\\n', '').replace(
                '\xa0 ', ',')

            #将当前用户的评论及评论时间，存储在字典Comment_dict中
            Comment_dict[User_ID] = Comment

    return Comment_dict


def get_hotel_comment(hotels_dict):
    #构建url访问评论页面

    #当前评论的页数
    comment_page = int(hotels_dict['Hotel_CommentCount'])//10

    #酒店ID
    ID = hotels_dict['Hotel_ID']


    #开10个线程，同时爬取目标网站数据
    with ThreadPoolExecutor(max_workers=10) as t:
        t.submit(get_comment_link, comment_page, ID)

        # 将酒店的评论页数和酒店ID，传给函数get_comment_link()函数
        Comment = get_comment_link(comment_page, ID)
        hotels_dict['Comment'] = Comment

    write_json(hotels_dict, hotels_dict['Hotel_Name'])


def get_index(url, data):
    #获取酒店信息，包括酒店名称

    #用于存储酒店信息
    hotels_dict = {}

    #定义请求头headers，避免被系统的反扒系统所识别
    headers = {
        'content-type': 'application/json;charset=UTF-8',
        'cookie': 'QN99=9149; QN1=eIQjml3TdwCQ3F2E/eGkAg==; QunarGlobal=10.86.213.150_5cfe31_16e8204577e_-3faf|1574139648925; _i=RBTKSNoofqwxkwKR6kVV2LZonQix; QN601=5b95fb1cad13f2ba85cb58e44f734cc7; QN48=69694751-b8b2-49a8-a2e5-cc139c4788eb; fid=fce2e90b-98b3-46a8-bfd6-c6aec371ed44; ls=%u4E09%u4E9A; QN235=2020-01-04; _RF1=221.182.236.68; _RSG=nVaqD6dYLKEv9CaZYXeC5A; _RDG=288a553fa479172dd4313042afba770c5e; _RGUID=e5158a71-8dd2-47f1-a14c-a218a390c279; __utmz=183398822.1578467420.7.7.utmcsr=hotel.qunar.com|utmccn=(referral)|utmcmd=referral|utmcct=/; Qs_lvt_55613=1578205121%2C1578237557%2C1578272053%2C1578314717%2C1578498829; Hm_lvt_8fa710fe238aadb83847578e333d4309=1576498705,1578143378,1578205122,1578498830; Qs_pv_55613=3930803083783042600%2C4037954834071853600%2C297172186538473200%2C157535779686491170%2C2689651625665552400; __utma=183398822.809776704.1578272055.1578467420.1578537643.8; QN57=15785575104240.33633514162768785; QN58=1578566582448%7C1578566844006%7C2; _jzqa=1.3021954660394055700.1574150419.1578537643.1578580072.23; _jzqx=1.1574150419.1578580072.6.jzqsr=hotel%2Equnar%2Ecom|jzqct=/.jzqsr=hotel%2Equnar%2Ecom|jzqct=/; QN73=3753-3762; _qzja=1.10014274.1574150418799.1578537643381.1578580072225.1578580542100.1578580688845..0.0.64.20; QN300=s%3Dbaidu; QN205=s%3Dbaidu; QN277=s%3Dbaidu; csrfToken=3oJn1EV2qx7c8TzvzR6NJFSJphekWIZP; QN163=0; QN269=71B88350308611EAAB12FA163E08FC6A; HN1=v1aee9abe6905b3408520c2950f25c8619; HN2=qnkrgqzulzsnc; cityUrl=sanya; cityName=%25E4%25B8%2589%25E4%25BA%259A; checkInDate=2020-04-03; checkOutDate=2020-04-30; QN267=864452964be50fb5f; _vi=rrxpfTilmm3MuuOQIIPQI1S5iA5p79byotAsywySLFMaMguXPak31DFUUI6KCryeHzioi6z6wYImijSyQmEg9KYjlAbTp7rSAykZi3ERnL3SEFLvGFaB_Bw456ZdIRjMDbyhJABMuTNPERauJ51y6Dl-MPh2j4d_f0Okm49Utio-; __qt=v1%7CVTJGc2RHVmtYMTljU0ZvYU9kYzMyQmNyZHVVZmpNNk9zRkJjV0hFSGJOSDIzblNQV1dLVDVCVXNhaEZoL2pOY21aTDlBaThVMDZrNkVsMGdIRHNadW9QQktmYVJpTlBxN1o0UEc1bDRMNzBORktObllDU0x4bSttQTBiWHBiMkx1V1dVbGViZ2d1UE95VTkrR2VEVnVJdUZHOVRzMGthWWViVVUyNHhJeXg0PQ%3D%3D%7C1585899627268%7CVTJGc2RHVmtYMStRVWJESFV2VTlPNHBXZ3pkeG1BTUhYanhNRHp6cDYvTUFHLzhoZUY1K2tteGlVcUlIMmlNUFMxZ1hkUGNsUEJmNk05bWFFTFVQclE9PQ%3D%3D%7CVTJGc2RHVmtYMStVcC9SZk9WYkN2MzcycU5ZeUVwdlloVnNBeC9QQUtnMVU2SU9TNHpTRVVDVmMycy8vWkY2akxWQ1k2YzhxLzF4K0pvV3BHU1FyOU9SSGhtL2JJeHlTenFqcDZXaHNVbGVUd1VweTBJMjY1dHIzc25qTEFxRyt0UTJSckRwZklPZDN6VWl2cVB3bHB0TFUxSUV6Q3VHY0Y2UTZYVFQ1VDFibUN3US9ZdjZSOGdFbDF4ZHVhYkdGSFdkQW04cWgxbXhvdG1Xb2tZb3RJTEZrdmFlNGk0T1R0cmhXUEkxbVBQUHhpaG52UmNqbjBTQjdmdFU5dmtwdmRNNVVSd2NlMWdSRWJQVW9uR0w5QWRFTysxdDNZK3BCS1IrM0dLRkdzc0MzU0hJSW5LVnVlb3BGZmZRcUw5WW1ONExFSzZvL25IZ29RRjJlZmZuekFSOUlmVk9jdDZLdjFHd0dEUTRVTlhUK0lNaXpxTkM1ZkNOcUhuNEZZQWJaQUFQazJhU1MvRUN0eUsyRXA5UjdsTmhxYWdoQzlKUjYxSVNVcHhzRGM1Mms1cGVYRk4wVTROeWI5SXlrR3dNK3RLWGxVMmQ3SllBRVpINUxzSmM5cnJGZlBQMEFaeXdrODk5Q0gxd21OOVBXNXg1T0N5eEIxUE5jWE4xTStnWStCbnB2M1dLM0VGSUcrNSs3QlZSTzZuNUhGU2pPUkFNMXFpWGw3VUp6cTdmUEFVeWxrOUZSUVdzR3crVDNqdjkrQmlEdzE3UVpZbzdtZy9xZjY3YlZ5S25XY1dTNk45bXUxOFNjRUljTzY5NWR0LzRvN0h0TXZ2L3c2TklLRjdHNjZuZmh2NHQ4bUNnYXdwSzI1K2M0dVpSQnliSHZGYSszWHp2K1AwcDBxSVU9; QN271=a171ba56-f7a9-4d72-8a13-3ba2bf3ea61b',
        'origin': 'https://hotel.qunar.com',
        'referer': 'https://hotel.qunar.com/cn/sanya/s00key17994793?fromDate=2020-04-03&toDate=2020-04-30',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    }

    html = requests.post(url, data = data, headers = headers)
    html.encoding = 'utf8'
    json_decoder = html.text
    start = json_decoder.find('{"data":')
    end = json_decoder.find('"des":"success"}}') + len('"des":"success"}}')
    result = json.loads(json_decoder[start: end])
    for r in result['data']['hotels']:

        #酒店名称
        hotels_dict['Hotel_Name'] =r['name']

        #酒店类型
        hotels_dict['Hotel_Type'] = r['dangciText']

        #酒店ID
        hotels_dict['Hotel_ID'] = r['seqNo'].replace('sanya_', '')

        #酒店评论数量
        hotels_dict['Hotel_CommentCount'] = r['commentCount']

        #酒店评分
        hotels_dict['Hotel_Score'] = r['score']

        #获取酒店的评论信息，将存储当前酒店信息的字典传给get_hotel_comment()函数
        get_hotel_comment(hotels_dict)
        # print(hotels_dict)






if __name__ == '__main__':
    url = 'https://hotel.qunar.com/napi/list'
    for i in range(0, 21, 20):
        data = {
            'b':{
                'bizVersion' : '17',
                'cityUrl' : 'sanya',
                'fromDate' : '2020-04-03',
                'toDate' : '2020-04-30',
                'q' : '海棠湾',
                'qFrom' : 3,
                'start' : '{}'.format(i),
                'num' : 20,
                'minPrice' : 0,
                'maxPrice': -1,
                'level': '5',
                'sort' : 0,
                'cityType': 1,
                'fromForLog' : 1,
                'searchType': 0,
                'locationAreaFilter': [],
                'comprehensiveFilter': []
            },
            'qrt' : 'h_hlist',
            'source': 'website'}
        #标准化
        data = json.dumps(data).encode(encoding='utf-8')
        get_index(url, data)