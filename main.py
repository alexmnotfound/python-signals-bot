"""
Signal Bot calculating SIMPLE PIVOTE POINTS and RSI
In this case, it calculates Monthly & Weekly pivotes and 15 min RSI with 30 & 70 limits.

If is close to a Pivot point, considering a tolerance (rtol), and RSI is below 30 or above 70, the signal is triggered.

It takes data from Google Sheets API and delivers signal through Telegram API

@author: alexmnotfound
"""

import datetime as dt
import pandas as pd
import config.binanceAPI as bp
import config.functions as fx
import config.sheets as sh

from config.telegramConn import sendMsg
from config.auth import telegramGroupID


def main():
    try:
        sendMsg(msg='== Initiating ==')
        print('Defining variables...\n')

        # To exec just for one day
        runtime = dt.datetime.now().day
        endtime = runtime + 1

        # Define parameters
        hourlyAlert = dt.datetime.now().hour    # I'm alive alert
        values = dict()                         # Empty Dict for future data

        tickers = sh.checkSheet()               # Tuple of tickers to check

        timeframes = ('1M', '1w')               # Tuple of timeframes to check
        pivots = 1                              # Quantity of pivots to check (current & prevs)
        tolerance = 0.3                         # Tolerance in price (percentage)
        waitingTime = 15                        # Minutes of rest between signals
        wait = 60 * waitingTime                 # Convertion of minutes to seconds

        # Send msg with parameters to control
        parameters = f'Tickers: {tickers}\n' \
                     f'Timeframes: {timeframes}\n' \
                     f'Pivots: {pivots}\n'
        #print(parameters)
        sendMsg(msg=parameters)

        # Creating dataframes' dictionaries with values to check for each timeframe
        # print('Creating Dictionaries..\n')
        sendMsg(msg='Creating Dictionaries..')

        # Creating excel that will contain dataframes to control.
        writer = pd.ExcelWriter('pivotes_multiples.xlsx', engine='xlsxwriter')

        # Check each ticker and timeframe to create Price DataFrame
        for ticker in tickers:
            # Creating sub dictionary for future data
            values[ticker[0]] = dict()

            for timeframe in timeframes:
                # Creating dataframe of prices and pivot points
                data = fx.priceDataframe(ticker=ticker, timeframe=timeframe, pivots=pivots)

                # Creating sheets of each one for excel document
                data.to_excel(writer, sheet_name=ticker[0] + '-' + timeframe)

                # Dropping unused columns
                data.drop(['Open', 'High', 'Low', 'Close'], axis=1, inplace=True)

                # Inserting data in sub dictionary
                values[ticker[0]][timeframe] = [data, wait]

        # Saving excel document
        writer.save()
        #print('Value Dictionaries created...')
        sendMsg(msg='Value Dictionaries created..')

        # Exec script just for one day
        while runtime != endtime:
            runtime = dt.datetime.now().day
            hourNow = dt.datetime.now().hour

            # Hourly alert
            if hourNow != hourlyAlert:
                sendMsg(msg="I'm still alive (lite)")
                hourlyAlert = hourNow

            # Controlling each ticker
            for ticker in tickers:

                # Searching current price of ticker and calculating tolerance
                price = bp.lastPrice(ticker=ticker[0])
                tol = price * (tolerance / 100)
                print(f'\nActual price {ticker}: {price}. Tolerance: {tol}')

                # Controlling each timeframe
                for timeframe in timeframes:

                    # Checking counter value to trigger signal (if True) for current ticker
                    counter = values[ticker[0]][timeframe][1]
                    print(f'Counter {timeframe}: {counter}')
                    if counter >= wait:

                        # Getting data of DataFrame for current ticker from values dictionary
                        data = values[ticker[0]][timeframe][0]

                        # Creating list of index for each True value in DataFrame (if found) for current ticker
                        indexes = fx.getIndexes(df=data, value=price, tolerance=tol)

                        # Triggers signal if value is found
                        if indexes:
                            # Check RSI
                            dataRsi = bp.historicData(symbol=ticker, interval='15m')
                            dataRsi = fx.addRSI(data=dataRsi)
                            rsi = dataRsi['rsi'].iloc[-1]

                            # Trigger signal is RSI is found
                            if rsi <= 30 or rsi >= 70:
                                if rsi <= 30:
                                    signal = 'Bullish signal on: '
                                elif rsi >= 70:
                                    signal = 'Bearish signal on: '

                                for index in indexes:
                                    # Convert numeric value of Timeframe to String
                                    pvTimeFrame = data["Timeframe"].loc[data.index == index[0]][0]
                                    pvTimeFrame = fx.getTimeframe(pvTimeFrame)

                                    # Creating signal's message
                                    msg = f'{signal}: {ticker[0]}\n' \
                                          f'Current Price: {price}\n' \
                                          f'Pivot Price: {data[index[1]].loc[data.index == index[0]][0]}\n' \
                                          f'Pivot: {index[1]}\n' \
                                          f'Timeframe: {pvTimeFrame}\n'

                                    sendMsg(ID=telegramGroupID, msg=msg)

                                    # Updating signals counter to zero
                                    values[ticker[0]][timeframe][1] = 0
                    else:
                        # Adding value to counter
                        values[ticker[0]][timeframe][1] += 1
        sendMsg(msg='...Ending Program...')
    except Exception as e:
        sendMsg(ID=telegramGroupID, msg=f'Me apagué por algún misterioso motivo: {e}')


if __name__ == '__main__':
    #sendMsg(ID=telegramGroupID, msg='Initiating bot')
    main()

