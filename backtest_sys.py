# -*- coding: utf-8 -*-
"""
@author: QiWu
"""

from function_lib import *
np.seterr(divide='ignore',invalid='ignore')

factor_name = 'ROE_neutral'

# 读取因子数据
factor = pd.read_csv(f'.\\Factor_realized\\{factor_name}.csv',
                     encoding='GBK', index_col='Unnamed: 0', parse_dates=['Unnamed: 0'])


# 回测
longshort = np.full((stockrate.shape[0]-1, 3),np.nan)
monotone = np.full((stockrate.shape[0]-1, 5),np.nan)
industry_distr = np.full((stockrate.shape[0] - 1, industry.shape[1]), np.nan)

for t in range(stockrate.shape[0]-1):
    Start = time.time()
    stockrate_t = np.array(stockrate.iloc[t+1,:]).reshape(-1,1)
    factor_t = np.array(factor.iloc[t, :]).reshape(-1,1)
    industry_distr[t, :] = get_industry_beta(factor_t)

    stockrate_t, factor_t, notnull = filter_null(stockrate_t, factor_t)
    if stockrate_t.shape[0] == 0:
        continue

    factor_group = group_stock(factor_t, 5)
    q1 = stockrate_t[factor_group == 1]
    q2 = stockrate_t[factor_group == 2]
    q3 = stockrate_t[factor_group == 3]
    q4 = stockrate_t[factor_group == 4]
    q5 = stockrate_t[factor_group == 5]
    benchmark = np.nanmean(stockrate_t)

    longshort[t,:] = np.array([nanmean_adj(q5), benchmark, nanmean_adj(q1)])
    monotone[t,:] = np.array([nanmean_adj(q1), nanmean_adj(q2), nanmean_adj(q3), nanmean_adj(q4), nanmean_adj(q5)])


    End = time.time()
    print(f'截面{factor.index[t]}计算完毕，用时{End-Start}s')

# 计算多空收益率
longshort = value_line(longshort)
longshort = pd.DataFrame(longshort, columns=['long','benchmark','short'])
longshort['long/benchmark'] = longshort['long']/longshort['benchmark']
longshort['benchmark/short'] = longshort['benchmark']/longshort['short']
longshort['long/short'] = longshort['long']/longshort['short']
longshort = pd.DataFrame(longshort.iloc[:,-3:]).set_index(stockrate.index[1:])

# 计算分组收益率、因子单调性
monotone_ = pd.DataFrame(value_line(monotone), columns=['quantile1', 'quantile2', 'quantile3', 'quantile4', 'quantile5'],
                         index=stockrate.index[1:])
monotone = pd.DataFrame(monotone, columns=['quantile1', 'quantile2', 'quantile3', 'quantile4', 'quantile5'])



# 计算因子衰减率
IC_decay_factor = calc_decay(factor,stockrate)

# 提取最后一个截面的因子值
last_distr = factor.iloc[-1,:]

# 提取行业暴露分布
industry_distr = pd.DataFrame(industry_distr, columns=industry.columns).apply(np.nanmean, axis=0)

# 画图
figures(longshort, monotone_, monotone.apply(np.nanmean, axis=0),
        IC_decay_factor, last_distr, industry_distr)