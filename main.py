import os, ssl
from datetime import time

from fyers_apiv3 import fyersModel
import pandas as pd
from fyers_apiv3.FyersWebsocket import data_ws
from login import login
import credentials as cred

# Disable SSL verification
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

login = login()
emadata = pd.DataFrame()
with open('access.txt', 'r') as a:
    tk = a.read()
# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=cred.client_id, is_async=False, token=tk, log_path="")

# variables
buypos = 0
sellpos = 0
stoploss = 0
entry = 0
bflag = 0
sflag = 0
spos = 0
bpos = 0
exit = 0
target = 0
cstrike = ''
pstrike = ''
row = -2
expiry = 'NSE:BANKNIFTY24403'
sym = 'NSE:NIFTYBANK-INDEX'
gain = 0
fmflag = 0
fimflag = 0
emadata5 = pd.DataFrame()
emadata15 = pd.DataFrame()
date_from = '2024-04-01'
date_to = '2024-04-09'


# get data function
def getdata(sym, res, rfrom, rto):
    global emadata5, emadata15
    cdata = {
        "symbol": sym,
        "resolution": str(res),
        "date_format": "1",
        "range_from": rfrom,
        "range_to": rto,
        "cont_flag": "0"
    }
    response = fyers.history(data=cdata)
    data = pd.DataFrame.from_dict(response['candles'])
    cols = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    data.columns = cols
    data['datetime'] = pd.to_datetime(data['datetime'], unit="s")
    data['datetime'] = data['datetime'].dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata')
    data['datetime'] = data['datetime'].dt.tz_localize(None)
    data = data.set_index('datetime')
    data['ema'] = data['close'].ewm(span=5, min_periods=5).mean()
    if (res == 5):
        emadata5 = data
    if (res == 15):
        emadata15 = data


# on message function
def onmessage(message):
    # symb = message['symbol']
    # ltp = message['ltp']
    # print(message)
    t = time.localtime()
    cmin = time.strftime("%M", t)
    csec = time.strftime("%S", t)
    global buypos, sellpos, stoploss, exit, pstrike, cstrike, target, bflag, sflag, sym, fmflag, fimflag, bpos, spos, gain, entry
    if (int(cmin) % 5 == 0 and int(csec) >= 1 and fmflag == 0):
        print("5 ema data updated")
        getdata(sym, 5, '2023-01-09', '2023-01-11')
        fmflag = 1
        if (spos == 0):
            sflag = 0
    if (int(cmin) % 5 != 0 and fmflag == 1):
        fmflag = 0
    if (int(cmin) % 15 == 0 and int(csec) >= 1 and fimflag == 0):
        print("15 ema data updated")
        getdata(sym, 15, '2023-01-09', '2023-01-11')
        fimflag = 1
        if (bpos == 0):
            bflag = 0
    if (int(cmin) % 15 != 0 and fimflag == 1):
        fimflag = 0
    #     ema = emadata['ema'].iloc[-2]
    #     l =  emadata['low'].iloc[-2]
    print(f"{message}")
    if (emadata5['close'].iloc[row] > emadata5['ema'].iloc[row]
            and emadata5['high'].iloc[row] > emadata5['ema'].iloc[row]
            and emadata5['open'].iloc[row] > emadata5['ema'].iloc[row]
            and emadata5['low'].iloc[row] > emadata5['ema'].iloc[row]
            and message['ltp'] < emadata5['low'].iloc[row]):
        ltp = message['ltp']
        sp = int(round(ltp, -2))
        if (spos == 0 and sflag == 0):
            spos = sflag = 1
            entry = message['ltp']
            stoploss = emadata5['high'].iloc[row]
            target = message['ltp'] - ((emadata5['high'].iloc[row] - emadata5['low'].iloc[row]) * 3)
            print('sell entry')
            pstrike = expiry + str(sp) + "PE"
            # data = {
            #     "symbol": str(pstrike),
            #     "qty":15,
            #     "type":2,
            #     "side":1,
            #     "productType":"MARGIN",
            #     "limitPrice":0,
            #     "stopPrice":0,
            #     "validity":"DAY",
            #     "disclosedQty":0,
            #     "offlineOrder":False,
            #     }
            # print(f"entry {pstrike}")
            # response = fyers.place_order(data=data)
    if (emadata15['close'].iloc[row] < emadata15['ema'].iloc[row]
            and emadata15['high'].iloc[row] < emadata15['ema'].iloc[row]
            and emadata15['open'].iloc[row] < emadata15['ema'].iloc[row]
            and emadata15['low'].iloc[row] < emadata15['ema'].iloc[row]
            and message['ltp'] > emadata15['high'].iloc[row]):
        ltp = message['ltp']
        sp = int(round(ltp, -2))
        if (bpos == 0 and bflag == 0):
            bpos = bflag = 1
            entry = message['ltp']
            stoploss = emadata15['low'].iloc[row]
            target = message['ltp'] + ((emadata15['high'].iloc[row] - emadata15['low'].iloc[row]) * 1)
            print('buy entry')
            cstrike = expiry + str(sp) + "CE"
            # data = {
            #     "symbol": str(cstrike),
            #     "qty":15,
            #     "type":2,
            #     "side":1,
            #     "productType":"MARGIN",
            #     "limitPrice":0,
            #     "stopPrice":0,
            #     "validity":"DAY",
            #     "disclosedQty":0,
            #     "offlineOrder":False,
            #     }
            # print(f"entry {cstrike}")
            # response = fyers.place_order(data=data)
    if (spos == 1 and message['ltp'] > stoploss):
        gain += entry - stoploss
        spos = 0
        stoploss = 0
        entry = 0
        target = 0
        # data = {
        #     "symbol": str(pstrike),
        #     "qty":15,
        #     "type":2,
        #     "side":-1,
        #     "productType":"MARGIN",
        #     "limitPrice":0,
        #     "stopPrice":0,
        #     "validity":"DAY",
        #     "disclosedQty":0,
        #     "offlineOrder":False,
        #     }
        # print(f"entry {pstrike}")
        # response = fyers.place_order(data=data)
    if (spos == 1 and message['ltp'] <= target):
        gain += entry - target
        spos = 0
        stoploss = 0
        entry = 0
        target = 0
        # data = {
        #     "symbol": str(pstrike),
        #     "qty":15,
        #     "type":2,
        #     "side":-1,
        #     "productType":"MARGIN",
        #     "limitPrice":0,
        #     "stopPrice":0,
        #     "validity":"DAY",
        #     "disclosedQty":0,
        #     "offlineOrder":False,
        #     }
        # print(f"entry {pstrike}")
        # response = fyers.place_order(data=data)
    if (bpos == 1 and message['ltp'] < stoploss):
        gain += stoploss - entry
        bpos = 0
        stoploss = 0
        entry = 0
        target = 0
        # data = {
        #     "symbol": str(cstrike),
        #     "qty":15,
        #     "type":2,
        #     "side":-1,
        #     "productType":"MARGIN",
        #     "limitPrice":0,
        #     "stopPrice":0,
        #     "validity":"DAY",
        #     "disclosedQty":0,
        #     "offlineOrder":False,
        #     }
        # print(f"entry {cstrike}")
        # response = fyers.place_order(data=data)
    if (bpos == 1 and message['ltp'] >= target):
        gain += target - entry
        bpos = 0
        stoploss = 0
        entry = 0
        target = 0
        # data = {
        #     "symbol": str(cstrike),
        #     "qty":15,
        #     "type":2,
        #     "side":-1,
        #     "productType":"MARGIN",
        #     "limitPrice":0,
        #     "stopPrice":0,
        #     "validity":"DAY",
        #     "disclosedQty":0,
        #     "offlineOrder":False,
        #     }
        # print(f"entry {cstrike}")
        # response = fyers.place_order(data=data)


def onerror(message):
    print("Error:", message)


def onclose(message):
    print("Connection closed:", message)


def onopen():
    data_type = "SymbolUpdate"
    symbols = [sym]
    fyersdata.subscribe(symbols=symbols, data_type=data_type)
    fyersdata.keep_running()


# Replace the sample access token with your actual access token obtained from Fyers
access_token = cred.client_id + ":" + tk

# Create a FyersDataSocket instance with the provided parameters
fyersdata = data_ws.FyersDataSocket(
    access_token=access_token,  # Access token in the format "appid:accesstoken"
    log_path="",  # Path to save logs. Leave empty to auto-create logs in the current directory.
    litemode=True,  # Lite mode disabled. Set to True if you want a lite response.
    write_to_file=False,  # Save response in a log file instead of printing it.
    reconnect=True,  # Enable auto-reconnection to WebSocket on disconnection.
    on_connect=onopen,  # Callback function to subscribe to data upon connection.
    on_close=onclose,  # Callback function to handle WebSocket connection close events.
    on_error=onerror,  # Callback function to handle WebSocket errors.
    on_message=onmessage  # Callback function to handle incoming messages from the WebSocket.
)

# Establish a connection to the Fyers WebSocket
fyersdata.connect()
