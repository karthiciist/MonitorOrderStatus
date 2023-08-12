import json
import math
import requests
from fyers_api import accessToken, fyersModel
from flask import Flask, render_template, request, redirect, send_file, url_for
from flask import Flask
from flask import request
import webbrowser
import yfinance as yf
from ta.trend import ADXIndicator
import datetime
import pandas as pd
import time
import numpy as np
import yfinance as yf
# from stockstats import StockDataFrame
import pyodbc
import http.client
import configparser
import os

config_obj = configparser.ConfigParser()
config_obj.read("..\configfile.ini")

dbparam = config_obj["mssql"]
server = dbparam["Server"]
db = dbparam["db"]

fyersparam = config_obj["fyers"]
clientid = fyersparam["clientid"]


def check_order_status():
    # access_token = os.getenv('ocs_access_token')

    with open("../access_token.txt") as f:
        access_token = f.read()
        print(access_token)

    conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                          r'Server=' + server + ';'
                          'Database=' + db + ';'
                          'Trusted_Connection=yes;')  # integrated security

    cursor = conn.cursor()

    SQLCommand = "select orderid from  [OCSTrade].[dbo].[OCS_Bought]  where orderstatus = 'open'"
    cursor.execute(SQLCommand)
    buy_line_items = cursor.fetchall()

    orderid = buy_line_items[0][0]




    if orderid != "":

        # Check if the order is active in fyers

        fyers = fyersModel.FyersModel(client_id=clientid, token=access_token)

        data = {"id": orderid}

        response = fyers.orderbook(data=data)
        order_status_dictionary = eval(str(response))
        status_code = int(order_status_dictionary["orderBook"][0]["status"])



        if status_code == 1:
            order_status = 'cancelled'
        elif status_code == 2:
            order_status = 'filled'
        elif status_code == 3:
            order_status = 'notused'
        elif status_code == 4:
            order_status = 'open'
        elif status_code == 5:
            order_status = 'rejected'
        elif status_code == 6:
            order_status = 'open'
        elif status_code == 7:
            order_status = 'expired'
        else:
            order_status = "open"


        conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                              r'Server=' + server + ';'
                              'Database=' + db + ';'
                              'Trusted_Connection=yes;')  # integrated security

        cur = conn.cursor()
        print("update [OCSTrade].[dbo].[OCS_Bought] SET orderstatus = '" + order_status + "' where orderid = '" + str(orderid) + "'")
        cur.execute("update [OCSTrade].[dbo].[OCS_Bought] SET orderstatus = '" + order_status + "' where orderid = '" + str(orderid) + "'")
        conn.commit()
        print("buy update - Y")
        conn.close()

    else:
        print("No open orders")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while (True):
        try:
            time.sleep(5)
            check_order_status()
        except Exception as e:
            print("No orders in open status")
            continue

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
