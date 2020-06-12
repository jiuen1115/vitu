import requests
import json
import numpy as np
import pandas as pd
import h5
import pytz
from datetime import datetime
from vitu.utils.date_utils import get_total_dates
def kline_coinbase(start,end,granularity):
    url='https://api-public.sandbox.pro.coinbase.com/products/BTC-USD/candles'
    payload={
        'start': start,  #ISO 8601格式时间，如'2017-03-23T08:00:00.000Z'
        'end': end,
        'granularity':granularity  #以秒为单位的时间间隔，１分钟取值60 １小时取值3600 一天取值86400
    }
    #一次请求获得Ｋ线长度不超过300，可以多次反复请求
    r = requests.get(url,params=payload)
    klines=json.loads(r.text)
    return klines

if __name__=='__main__':
    exchange='coinbase'
    symbol='btcusd'
    freq='1d'
    start1='2017-01-01 00:00:00'
    end1='2020-05-31 00:00:00'
    start2=datetime.strptime(start1,'%Y-%m-%d %H:%M:%S').timestamp()
    end2=datetime.strptime(end1,'%Y-%m-%d %H:%M:%S').timestamp()
    length1=get_total_dates(freq,1,0,start1,end1)
    if freq == '1d':
       interval=86400
       count=round((end2-start2)/(lenght1-1))
    if count>1:   
       for i in range(count)
           
    data1=kline_coinbase('2017-03-23T08:00:00.000Z','2017-12-23T08:00:00.000Z',86400)
    df=data1.sort_index(axis=0,by='date',ascending=True)

    years = dict()
    for i in range(len(df)):
        year = (datetime.strptime(df.iloc[i]['date'],'%Y-%m-%d %H:%M:%S')).year
        if year not in years:
            years[year] = list()
        tempdata1= (df.iloc[i][1:7].values) 
        tempdata1[0]=datetime.strptime(df.iloc[i]['date'],'%Y-%m-%d %H:%M:%S')
        tempdata=tuple(tempdata1)
        years[year].append(tempdata)

    max_time = None
    for year in years:
        f = h5.get_file_w(exchange, symbol, freq, str(year))
        try:
            dset = f.get_create_ohlcv(freq)
            for i in years[year]:
                # dset[i[0].timetuple().tm_yday-1] = (int(i[0].replace(tzinfo=pytz.timezone('utc')).timestamp()), i[1], i[2], i[3], i[4], i[5])
                #60min
                d = i[0]
                dset[(d.timetuple().tm_yday - 1) * 24 + (d.timetuple().tm_hour) * 1 ] = (int(i[0].replace(tzinfo=pytz.timezone('utc')).timestamp()), i[1], i[2], i[3], i[4], i[5])
                if max_time is None:
                    max_time = i[0]
                else:
                    max_time = max(max_time, i[0])
        finally:
            f.close()

# #获取k线数据
# def getklines(count,endTime):
#     #参考http://aijiebots.com/wenzhang/80
#     url = 'https://www.bitmex.com/api/v1/trade/bucketed'
#     payload = {
#         'binSize':'1d', #时间周期，可选参数包括1m,5m,1h,1d
#         'partial':'false', #是否返回未完成的K线
#         'symbol':'XBTUSD', #合约类型，如永续合约:XBTUSD
#         'count':count, #返回K线的条数
#         'reverse':'true', #是否显示最近的数据，即按时间降序排列
#         'endTime':endTime #结束时间，格式：2018-07-23T00:00:00.000Z
# #        'startTime':startTime #开始时间，格式：2018-06-23T00:00:00.000Z
#     }
#     r = requests.get(url,params=payload)
#     klines = json.loads(r.text)
#     return klines
#     # for kline in klines:
#     #     print(kline)

# if __name__=='__main__':
#     data1=getklines(1000,'2020-05-30T00:00:00.000Z')
import json
from vitu import api 
import numpy as np
import pandas as pd
import h5
import pytz
from datetime import datetime
data=api.coinbar(symbol='xbt',contract_type='perpetual',exchange='future_bitmex',freq='60min',start_date='2018-01-01 00:00:00',end_date='2018-12-31 00:00:00')
# data=api.coinbar(symbol='btcusd',exchange='kraken',freq='daily',start_date='2017-05-01',end_date='2017-05-31')
df=data.sort_index(axis=0,by='date',ascending=True)
exchange='bitmex'
symbol='xbtusd'
freq='1h'
years = dict()
for i in range(len(df)):
    year = (datetime.strptime(df.iloc[i]['date'],'%Y-%m-%d %H:%M:%S')).year
    if year not in years:
        years[year] = list()
    tempdata1= (df.iloc[i][1:7].values) 
    tempdata1[0]=datetime.strptime(df.iloc[i]['date'],'%Y-%m-%d %H:%M:%S')
    tempdata=tuple(tempdata1)
    years[year].append(tempdata)

max_time = None
for year in years:
    f = h5.get_file_w(exchange, symbol, freq, str(year))
    try:
        dset = f.get_create_ohlcv(freq)
        for i in years[year]:
            # dset[i[0].timetuple().tm_yday-1] = (int(i[0].replace(tzinfo=pytz.timezone('utc')).timestamp()), i[1], i[2], i[3], i[4], i[5])
            #60min
            d = i[0]
            dset[(d.timetuple().tm_yday - 1) * 24 + (d.timetuple().tm_hour) * 1 ] = (int(i[0].replace(tzinfo=pytz.timezone('utc')).timestamp()), i[1], i[2], i[3], i[4], i[5])
            if max_time is None:
                max_time = i[0]
            else:
                max_time = max(max_time, i[0])
    finally:
        f.close()

# filename ='bitmexdata1.json'
# with open(filename,'w') as f :
#     json.dump(df,f)
