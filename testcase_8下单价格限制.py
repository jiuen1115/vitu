from vitu import ai, api, log
import numpy as np

import os
#配置数据导入地址
os.environ["H5_ROOT_DIR"]="/home/john/Downloads/datah5/bundle" #"D:/datah5_m/bundle"
print(os.path.exists(os.environ["H5_ROOT_DIR"]))  #返回True，则数据导入成功
# 配置单/多账户初始持仓信息
ai.create_account(name='account_name_1', exchange='binance', account_type='digital.spot', position_base=[{'asset': 'BTC', 'qty': 10},{'asset': 'USDT', 'qty': 200000}])
ai.create_account(name='account_name_2', exchange='binance', account_type='digital.spot', position_base=[{'asset': 'ETH', 'qty': 200},{'asset': 'USDT', 'qty': 200000}])

# 可以直接指定universe，或者通过筛选条件选择universe池,这里直接指定binance交易所的BTC/USDT、ETH/USDT
universe = ai.create_universe(['BTC/USDT.binance','ETH/USDT.binance'])

# initialize方法：设置策略当中会用到的参数，在handle_data方法中可以随时调用
def initialize(context):
    #我们在这里配置MA策略使用的均线窗口大小和账户对象信息
    context.MA_length = 10
    context.account_1 = context.get_account('account_name_1')
    context.account_2 = context.get_account('account_name_2')

# handle_data方法：主要策略逻辑，universe数据将会触发此段逻辑，例如日线历史数据或者是实时数据
def handle_data(context):
			# 获取binance交易所的BTC/USDT最新价格
    current_price_1 = context.get_price("BTC/USDT.binance")
    # 每天买入0.2BTC
    context.account_1.buy("BTC/USDT.binance", current_price_1*0.99, 0.2)
    
    # 获取binance交易所的ETH/USDT最新价格
    current_price_2 = context.get_price("ETH/USDT.binance")
    # 每天卖出0.2ETH
    context.account_2.sell("ETH/USDT.binance", current_price_2*0.99, 0.2)
        
# 配置策略参数如：基准、回测数据级别等
my_strategy = ai.create_strategy(
    initialize,
    handle_data,
    universe=universe,
    benchmark='csi5',
    freq='1d',
    refresh_rate=1
)

# 配置回测参数如：回测日期、手续费率
ai.backtest(strategy=my_strategy,
         start='2018-12-10',
            end='2019-08-10',
            commission={'taker': 0.0002, 'maker': 0.0002}
            )