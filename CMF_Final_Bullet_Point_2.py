import pandas as pd
import numpy as np
import os

os.chdir(r'/Users/mihne/Desktop/MSc/Summer Term/ATS/Backtesting') # Change Directory

# Get commodities and sectors data
cmdty = pd.read_excel("Commodity Data.xlsx", sheet_name = "Return indices").set_index("date")

# Calculate daily returns
try:
    returns = pd.read_csv("Commodity_Returns.csv").set_index("date")
except FileNotFoundError:
    returns = cmdty/cmdty.shift(1)
    returns.to_csv("Commodity_Returns.csv")

lastIndex = cmdty.shape[0]  #Get index number of last observation

# Create empty dataframe to store Commodity Market Factor (CMF) data
CMF = pd.DataFrame(columns = ['CMF Returns'], index = returns.index.copy())

# CMF Returns
for i in range(0,lastIndex):
    non_zero_returns = returns.iloc[i][returns.iloc[i].notnull()]
    CMF.iloc[i]['CMF Returns'] = (non_zero_returns).mean()  # Commodity Market Factor = equal weighted return of all commodities traded during a single day

# CMF Prices (Derive commodity market factor price implied by the cumulative returns of the underlying commodities - series starts at 100.00)
CMF['CMF Prices'] = CMF.cumprod()*100

# Create empty dataframe to store CMF summary stats 
summary_stats_CMF = pd.DataFrame(columns = ['CMF'], 
                             index=['First Obs Date','No Obs','Tot Ret (%)','Avg Ret (%)', \
                                    'SD (%)', 'Sharpe', 'Skew', 'Kurtosis', 'HWM', 'HWM Date', \
                                    'MDD (%)', 'Peak Date', 'Trough Date', 'Inv. Calmar Ratio'])

# Number of Observations
summary_stats_CMF.loc['No Obs'] = CMF['CMF Returns'].count()

# Total Return (cumulative)
summary_stats_CMF.loc['Tot Ret (%)'] = ((CMF['CMF Returns'].cumprod().iloc[lastIndex-1])-1)*100

# Date of first observation
summary_stats_CMF.loc['First Obs Date'] = CMF.loc[CMF['CMF Prices'].first_valid_index()].name
        
# Average Return
summary_stats_CMF.loc['Avg Ret (%)'] = (CMF['CMF Returns']-1).mean()*252*100

# Standard Deviation
summary_stats_CMF.loc['SD (%)'] = CMF['CMF Returns'].std() * np.sqrt(252) * 100

# Sharpe (Note: returns are already in excess of the risk free rate)
summary_stats_CMF.loc['Sharpe'] = summary_stats_CMF.loc['Avg Ret (%)'] / summary_stats_CMF.loc['SD (%)']

# Skewness
summary_stats_CMF.loc['Skew'] = CMF['CMF Returns'].skew()

# Kurtosis
summary_stats_CMF.loc['Kurtosis'] = CMF['CMF Returns'].kurt()

## Calculating cumulative returns of the CMF

CMF['CMF Cum Returns'] = CMF['CMF Returns'].cumprod()

# HWM and HWM Date (High Water Mark)
summary_stats_CMF.loc['HWM'] = CMF['CMF Prices'].max()
CMF = CMF.apply(pd.to_numeric, errors = 'coerce')  # object to float64
summary_stats_CMF.loc['HWM Date'] = CMF['CMF Prices'].idxmax()

# MDD (Maximum Drawdown)
DD = CMF["CMF Prices"].cummax() - CMF["CMF Prices"]
end_mdd = DD.idxmax()
start_mdd = CMF["CMF Prices"][:end_mdd].idxmax()
summary_stats_CMF.loc['Peak Date'] = start_mdd
summary_stats_CMF.loc['Trough Date'] = end_mdd
summary_stats_CMF.loc['MDD (%)'] = (1-CMF['CMF Cum Returns'][end_mdd]/CMF['CMF Cum Returns'][start_mdd])*100

# Inverse Calmar Ratio
summary_stats_CMF.loc['Inv. Calmar Ratio'] = summary_stats_CMF.loc['MDD (%)'] / summary_stats_CMF.loc['Avg Ret (%)']

# Rounding (float numbers)
summary_stats_CMF.loc['Tot Ret (%)'] = summary_stats_CMF.loc['Tot Ret (%)'].apply(lambda x : round(x,2))
summary_stats_CMF.loc['Avg Ret (%)'] = summary_stats_CMF.loc['Avg Ret (%)'].apply(lambda x : round(x,2))
summary_stats_CMF.loc['SD (%)'] = summary_stats_CMF.loc['SD (%)'].apply(lambda x : round(x,2))
summary_stats_CMF.loc['Sharpe'] = summary_stats_CMF.loc['Sharpe'].apply(lambda x : round(x,2))
summary_stats_CMF.loc['Skew'] = summary_stats_CMF.loc['Skew'].apply(lambda x : round(x,2))
summary_stats_CMF.loc['HWM'] = summary_stats_CMF.loc['HWM'].apply(lambda x : round(x,2))
summary_stats_CMF.loc['Kurtosis'] = summary_stats_CMF.loc['Kurtosis'].apply(lambda x : round(x,2))
summary_stats_CMF.loc['MDD (%)'] = summary_stats_CMF.loc['MDD (%)'].apply(lambda x : round(x,2))
summary_stats_CMF.loc['Inv. Calmar Ratio'] = summary_stats_CMF.loc['Inv. Calmar Ratio'].apply(lambda x : round(x,2))

print(summary_stats_CMF)
# Export transposed summary stats dataframe to csv
(summary_stats_CMF.T).to_csv('CMF_Stats_Final.csv')
