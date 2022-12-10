"""
@author: QiWu
"""

from function_lib import *

# 以构建市值、行业中性化的ROE因子为例
mktcap = pd.read_csv('C:\\PKU大四上\\当代量化交易系统的原理与实现\\编写交易系统\\Data\\mktcap.csv',
                         encoding='GBK', index_col='Unnamed: 0')

ROE = pd.read_csv('C:\\PKU大四上\\当代量化交易系统的原理与实现\\编写交易系统\\Data\\ROE.csv',
                  encoding='GBK', index_col='Unnamed: 0')

# 构建策略、
start = time.time()

factor_temp = np.full(ROE.shape, np.nan)
for t in range(ROE.shape[0]):
    start = time.time()

    factor_t = np.array(ROE.iloc[t, :]).reshape(-1, 1)
    mktcap_t = np.array(mktcap.iloc[t, :]).reshape(-1, 1)
    # 调用中性化函数，对市值、行业做中性化处理
    factor_t = neutral(factor_t, mktcap_t)
    factor_t = neutral(factor_t, industry.iloc[:, :-1])
    factor_temp[t, :] = factor_t[:, 0]

    end = time.time()
    print(f'{ROE.index[t]}计算完成，用时{end - start}s')



# 截尾与标准化处理
factor_temp = winsorize(factor_temp, 5)
factor_temp = pd.DataFrame(factor_temp, index=ROE.index).apply(standardize, axis=1)

factor_temp.to_csv('.\\Factor_realized\\ROE_neutral.csv', encoding='GBK')
