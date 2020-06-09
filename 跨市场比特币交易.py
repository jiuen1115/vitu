from vitu import ai, api, log
import numpy as np
import os
#配置数据导入地址
os.environ["H5_ROOT_DIR"]="/home/john/Downloads/data/opt/data/vitu/bundle" #"D:/datah5_m/bundle"
print(os.path.exists(os.environ["H5_ROOT_DIR"]))  #返回True，则数据导入成功
# 配置单/多账户初始持仓信息
ai.create_account(name='binance', exchange='binance', account_type='digital.spot', position_base=[{'asset': 'BTC', 'qty': 1}])
ai.create_account(name='poloniex', exchange='poloniex', account_type='digital.spot', position_base=[{'asset': 'BTC', 'qty': 1}])

# 可以直接指定universe，或者通过筛选条件选择universe池,这里直接指定binance交易所的BTC/USDT、ETH/USDT
universe = ai.create_universe(['BTC/USDT.binance','BTC/USDT.poloniex'])
accounts = {}

# initialize方法：设置策略当中会用到的参数，在handle_data方法中可以随时调用
def initialize(context):

    for ticker in universe:
      account_name = ticker.split('.')[-1]
      accounts[account_name] = context.get_account(account_name)
      

# handle_data方法：主要策略逻辑，universe数据将会触发此段逻辑，例如日线历史数据或者是实时数据
def handle_data(context):

    universe_price_list = [(ticker, context.get_price(ticker)) for ticker in universe]
    cheap_btc_ticker = sorted(universe_price_list, key=lambda d: d[1])[0][0]
    print(universe_price_list)
    print('cheap:', cheap_btc_ticker)
    
    for ticker, current_price in universe_price_list:
        account_name = ticker.split('.')[-1]
        print(current_price)
        if current_price == 0 or np.isnan(current_price):
          print('price is error', ticker)
          continue
        
        if cheap_btc_ticker == ticker:
            amount = accounts[account_name].get_position('USDT')['available']/current_price
            if amount < 0.001:
              continue
            log.info(('buy:', cheap_btc_ticker, account_name, current_price, amount))
            accounts[account_name].buy(ticker, current_price, amount*0.99)
        else:
            amount = accounts[account_name].get_position('BTC')['available']
            if amount < 0.001:
              continue
            log.info(('sell:', cheap_btc_ticker, ticker, account_name, current_price, amount))
            accounts[account_name].sell(ticker, current_price, amount*0.99)

        
# 配置策略参数如：基准、回测数据级别等
my_strategy = ai.create_strategy(
    initialize,
    handle_data,
    universe=universe,
    benchmark='csi5',
    freq='d',
    refresh_rate=1
)

# 配置回测参数如：回测日期、手续费率
ai.backtest(strategy=my_strategy,
         start='2018-03-10',
            end='2018-05-29',
            commission={'taker': 0.0002, 'maker': 0.0002}
            )