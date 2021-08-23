def pivotsCalculation(df):
    '''
    Calculate Pivot Points from price DataFrame with OHLC.

    :param df: DataFrame with OHLC (Open, High, Low, Close)
    :return:
    '''
    try:
        df['PP'] = (df.High.shift(1) + df.Low.shift(1) + df.Close.shift(1)) / 3
        df['R1'] = (2 * df.PP) - df.Low.shift(1)
        df['R2'] = df.PP + (df.High.shift(1) - df.Low.shift(1))
        df['R3'] = df.High.shift(1) + (2 * (df.PP - df.Low.shift(1)))
        df['S1'] = (2 * df.PP) - df.High.shift(1)
        df['S2'] = df.PP - (df.High.shift(1) - df.Low.shift(1))
        df['S3'] = df.Low.shift(1) - (2 * (df.High.shift(1) - df.PP))

    except Exception as e:
        print(f'Dataframe can not be processed: {e}')

    '''
    Formula:

    df['PP'] = (df.High + df.Low + df.Close) / 3
    df['R1'] = (2 * df.PP) - df.Low
    df['R2'] = df.PP + (df.High - df.Low)
    df['R3'] = df.High + (2 * (df.PP - df.Low))
    df['S1'] = (2 * df.PP) - df.High
    df['S2'] = df.PP - (df.High - df.Low)
    df['S3'] = df.Low - (2 * (df.High - df.PP))
    '''
    return df
