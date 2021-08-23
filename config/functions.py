import numpy as np
import src.config.binanceAPI as bp
import src.config.pivotPoints as pv


def priceDataframe(ticker, timeframe, pivots=3):
    """
    Creates a DataFrame with historic OHLC for a given ticker (symbol) and timeframe

    :param ticker: symbol (BTC, ETH, LTC, etc.)
    :param timeframe: timeframe (1d, 1w, 1M)
    :param pivots: quantity of pivote points to calculate
    :return: DataFrame with OHLC & pivot points
    """
    # Download historic data of prices (OHLC from binance)
    data = bp.historicData(ticker, interval=timeframe)[['Open', 'High', 'Low', 'Close']]
    data = data.tail(pivots + 1)

    # Pivot points calculation
    data = pv.pivotsCalculation(data)
    data = round(data, 2)
    data = data.tail(pivots)

    # Timeframe handling to numeric value
    if timeframe == '1d':
        data['Timeframe'] = 1
    elif timeframe == '1w':
        data['Timeframe'] = 7
    elif timeframe == '1M':
        data['Timeframe'] = 30

    return data


def getIndexes(df, value, tolerance):
    """
    Create list with DataFrame index values where an approximate price is found.


    :param df:  DataFrame with values to check
    :param value:  price
    :param tolerance:  price tolerance
    :return: Index list

    Credits: https://thispointer.com/python-find-indexes-of-an-element-in-pandas-dataframe/
    """

    # Create empty list for future index data
    listOfPos = list()

    # Convert DataFrame values to boolean if price is close
    result = df.apply(np.isclose, b=value, atol=tolerance)

    # Getting column list with True values
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)

    # Iterating over columns list with True Value and getting lines where such value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append((row, col))

    # Return Tuple with positions of True value of DataFrame
    return listOfPos


def getTimeframe(timeframe):
    """
    Convertion of timeframe value to Text
    """
    if timeframe == 1:
        return 'Diario'
    elif timeframe == 7:
        return 'Semanal'
    elif timeframe == 30:
        return 'Mensual'


def addRSI(data, length=14, length_pend=0):
    """
    Insert RSI column in DF based con Close

    :param data: DataFrame
    :param ruedas: Integer, quantity of candles for RSI calculation
    :param ruedas_pend: Integer (optional), quantity of candles for RSI Pendant and Divergente calculation
    :return:
    """
    import numpy as np
    df = data.copy()
    df['dif'] = df.Close.diff()
    df['win'] = np.where(df['dif'] > 0, df['dif'], 0)
    df['loss'] = np.where(df['dif'] < 0, abs(df['dif']), 0)
    df['ema_win'] = df.win.ewm(alpha=1 / length).mean()
    df['ema_loss'] = df.loss.ewm(alpha=1 / length).mean()
    df['rs'] = df.ema_win / df.ema_loss
    data['rsi'] = round(100 - (100 / (1 + df['rs'])))

    if length_pend != 0:
        data['rsi_pend'] = (data.rsi / data.rsi.shift(length_pend) - 1) * 100
        precio_pend = (data.Close / data.Close.shift(length_pend) - 1) * 100
        data['rsi_div'] = data.rsi_pend * precio_pend
    return data
