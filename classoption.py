import requests
import pandas as pd
from pandas.io.json._normalize import json_normalize
import json
from openpyxl import Workbook
import numpy as np
from scipy.stats import norm
import datetime


class OptionChainData:
    def __init__(self):

        self.url_nf = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
        self.url_oc = "https://www.nseindia.com/option-chain"
        self.url_bnf = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'

        self.url_indices = "https://www.nseindia.com/api/allIndices"

        # Headers
        self.headers ={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

        self.session = requests.Session()
        request = self.session.get(self.url_oc, headers=self.headers, timeout=100)
        self.cookies = dict(request.cookies)
        # Set cookies
        self.session.cookies.update({'cookie_name': 'cookie_value'})

        # Make request
        self.response = self.session.get(self.url_nf, headers=self.headers)
        self.data = self.response.json()
        self.pe_oi = []
        self.result = self.analyse_atm()

    def write_to_file(self):
        if self.data:  # Check if self.data is not None or empty
            with open('data.json', 'w') as dat:
                json.dump(self.data, dat)
            print("Data successfully written to data.json")
        else:
            print("No data available to write. Check the API response.")

    def fetch_data(self):
        self.DATA = self.data['filtered']['data']

    def create_dataframe(self):
        self.DATAFRAME = pd.DataFrame()

    def add_data_to_df(self, name, pe_or_ce, element):
        data_name = []

        for i in self.DATA:
            column_data = i[pe_or_ce][element]
            data_name.append(column_data)

        self.DATAFRAME[name] = data_name
    def max_pain(self):
        '''Calculating Max pain point for both call and put sides'''
        # Group the call data by strike price and sum the open interest
        self.ce_grouped = self.DATAFRAME.groupby('strike_price')['ce_open_interest'].sum()

        # Calculate the max pain point by finding the strike price with the highest open interest
        self.ce_max_pain_point = self.ce_grouped.idxmax()

        # Group the put data by strike price and sum the open interest
        self.pe_grouped = self.DATAFRAME.groupby('strike_price')['pe_open_interest'].sum()

        # Calculate the max pain point by finding the strike price with the highest open interest
        self.pe_max_pain_point = self.pe_grouped.idxmax()

        print("Call option Max Pain Point:", self.ce_max_pain_point)
        print("put option Max Pain Point:", self.pe_max_pain_point)
        self.DATAFRAME.to_excel('option chain.xlsx', index=False)
        max = [self.ce_max_pain_point,self.pe_max_pain_point]
        return max


    def analyse_atm(self):
        # Analysing atm options
        # Load option chain data into a DataFrame
        self.df = pd.read_excel('option chain.xlsx')
        underlying_price = self.df.at[4, 'underlying_price']
        self.df2 = self.df[self.df['strike_price'] <= (underlying_price + 100)]
        self.df3 = self.df[self.df['strike_price'] >= (underlying_price - 100)]
        # Compare the two DataFrames and keep only the rows that are the same
        self.same_rows = self.df2[self.df2.isin(self.df3).all(1)]
        # with the help of change in premiums and open interests assuming sellers and buyers activity
        ce_change_in_oi = self.same_rows['ce_chng_in open_interest'].sum(numeric_only=False)
        ce_change_ltp = self.same_rows['ce_chng_LTP'].sum(numeric_only=False)
        pe_change_in_oi = self.same_rows['pe_chng_in open_interest'].sum(numeric_only=False)
        pe_change_ltp = self.same_rows['pe_chng_LTP'].sum(numeric_only=False)
        res = []
        if ce_change_in_oi >= 0 and ce_change_ltp >= 0:
            res.append("call buyers are active")
        if ce_change_in_oi >= 0 and ce_change_ltp <= 0:
            res.append("call sellers are active")
        if ce_change_in_oi <= 0 and ce_change_ltp >= 0:
            res.append("call sellers are closing positions")
        if ce_change_in_oi <= 0 and ce_change_ltp <= 0:
           res.append("call buyers are closing position")

        if pe_change_in_oi >= 0 and pe_change_ltp >= 0:
            res.append("put buyers are active")
        if pe_change_in_oi >= 0 and pe_change_ltp <= 0:
            res.append("put sellers are active")
        if pe_change_in_oi <= 0 and pe_change_ltp >= 0:
            res.append("put sellers are closing positions")
        if pe_change_in_oi <= 0 and pe_change_ltp <= 0:
            res.append("put buyers are closing position")
        self.same_rows.to_excel('atm.xlsx', index=False)
        return res

    def call_all_functions(self):
        self.write_to_file()
        self.fetch_data()
        self.create_dataframe()
        self.add_data_to_df(name='ce_open_interest', pe_or_ce='CE', element='openInterest')
        self.add_data_to_df(name='expiry_date', pe_or_ce='CE', element='expiryDate')
        self.add_data_to_df(name='ce_chng_in open_interest', pe_or_ce='CE', element='changeinOpenInterest')
        self.add_data_to_df(name='ce_volume', pe_or_ce='CE', element='totalTradedVolume')
        self.add_data_to_df(name='ce_IV', pe_or_ce='CE', element='impliedVolatility')
        self.add_data_to_df(name='ce_LTP', pe_or_ce='CE', element='lastPrice')
        self.add_data_to_df(name='ce_chng_LTP', pe_or_ce='CE', element='change')
        self.add_data_to_df(name='ce_buy_qty', pe_or_ce='CE', element='totalBuyQuantity')
        self.add_data_to_df(name='ce_sell_qty', pe_or_ce='CE', element='totalSellQuantity')
        self.add_data_to_df(name='ce_bid_qty', pe_or_ce='CE', element='bidQty')
        self.add_data_to_df(name='ce_bid_price', pe_or_ce='CE', element='bidprice')
        self.add_data_to_df(name='ce_ask_price', pe_or_ce='CE', element='askPrice')
        self.add_data_to_df(name='ce_ask_qty', pe_or_ce='CE', element='askQty')
        self.add_data_to_df(name='strike_price', pe_or_ce='CE', element='strikePrice')
        self.add_data_to_df(name='underlying_price', pe_or_ce='CE', element='underlyingValue')
        self.add_data_to_df(name='pe_bid_qty', pe_or_ce='PE', element='bidQty')
        self.add_data_to_df(name='pe_bid_price', pe_or_ce='PE', element='bidprice')
        self.add_data_to_df(name='pe_ask_price', pe_or_ce='PE', element='askPrice')
        self.add_data_to_df(name='pe_ask_qty', pe_or_ce='PE', element='askQty')
        self.add_data_to_df(name='pe_chng_LTP', pe_or_ce='PE', element='change')
        self.add_data_to_df(name='pe_LTP', pe_or_ce='PE', element='lastPrice')
        self.add_data_to_df(name='pe_IV', pe_or_ce='PE', element='impliedVolatility')
        self.add_data_to_df(name='pe_volume', pe_or_ce='PE', element='totalTradedVolume')
        self.add_data_to_df(name='pe_chng_in open_interest', pe_or_ce='PE', element='changeinOpenInterest')
        self.add_data_to_df(name='pe_open_interest', pe_or_ce='PE', element='openInterest')
        self.max_pain()
        self.analyse_atm()













