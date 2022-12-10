# -*- coding: utf-8 -*-
"""
@author: QiWu
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import time
from sklearn.linear_model import LinearRegression

# 数据处理函数

def winsorize(data, n):
    '''
    对数据进行截尾处理
    :param data: 2darray，按行处理
    :param n: 标准差倍数
    :return: 截尾后的数据，2darray
    '''
    data_ = data.copy()
    a = np.nanmean(data_, axis=1)
    b = np.nanstd(data_, axis=1)
    anb_p = np.hstack([(a + n * b).reshape(-1, 1)] * data_.shape[1])
    anb_n = np.hstack([(a - n * b).reshape(-1, 1)] * data_.shape[1])
    while data_[data_ > anb_p].shape[0] > 0 or data_[data_ < anb_n].shape[0] > 0:
        data_[data_ > anb_p] = anb_p[data_ > anb_p]
        data_[data_ < anb_n] = anb_n[data_ < anb_n]
        a = np.nanmean(data_, axis=1)
        b = np.nanstd(data_, axis=1)
        anb_p = np.hstack([(a + n * b).reshape(-1, 1)] * data_.shape[1])
        anb_n = np.hstack([(a - n * b).reshape(-1, 1)] * data_.shape[1])
    return data_


def standardize(data):
    '''
    对数据进行标准化处理，调用时需apply
    :param data: 1darray
    :return: 标准化后的数据，1darray
    '''
    if np.nanstd(data) != 0:
        return (data - np.nanmean(data)) / np.nanstd(data)
    else:
        return data - np.nanmean(data)


def filter_null(y, x):
    '''
    删去数据中缺失值，仅保留都有数据的样本，以便进行回归等操作
    :param y: ndarray，与x行数/shape[0]相同
    :param x: ndarray，与y行数/shape[0]相同
    :return: 处理好的y，x，及非空部分的坐标
    '''
    notnull = (~np.isnan(np.hstack([y, x]))) * (~np.isinf(np.hstack([y, x])))
    y_ = y[notnull.all(axis=1)]
    x_ = x[notnull.all(axis=1)]
    return y_, x_, notnull.all(axis=1)


def fill_by_mean(ser):
    '''
    以均值填充缺失值
    :param ser: pd.Series
    :return: 填充后的pd.Series
    '''
    if np.isnan(ser).all():
        return np.nan
    else:
        mean = np.nanmean(ser)
        return ser.fillna(mean)


def onehot(data, column):
    '''
    分类变量转化为one hot矩阵/虚拟变量
    :param data:含有分类变量的数据
    :param column: 分类变量列名
    :return: onehot矩阵
    '''
    onehot = pd.get_dummies(data, columns=[column])
    return onehot.iloc[:, 1:]


def nanmean_adj(data):
    '''
    解决np.nanmean遇到全空矩阵时的warning
    '''
    if np.isnan(data).all():
        return np.nan
    else:
        return np.nanmean(data)


# 功能函数

def neutral(F, neutralF):
    '''
    截面上对因子进行中性化处理
    :param F: 2darray
    :param neutralF: 2darray
    :return: 中性化后的因子F，即残差
    '''
    residual = np.full(F.shape, np.nan)
    m = LinearRegression()
    F_, neutralF_, notnull_ind = filter_null(F,neutralF)
    m.fit(neutralF_,F_)
    residual[notnull_ind] = F_ - m.predict(neutralF_)
    return residual


def get_industry_beta(F):
    '''
    计算因子在行业上的风险暴露
    :param F: 2darray
    :return: 风险暴露
    '''
    m = LinearRegression()
    F_, neutralF_, notnull_ind = filter_null(F,industry)
    m.fit(neutralF_,F_)
    return m.coef_


def group_stock(ser, n):
    '''
    分组函数,为股票分组以观测每组收益
    :param ser: pd.Series
    :param n: 所分组数
    '''
    ser_ = ser.copy()
    ser_[ser <= np.nanquantile(ser, 1 / n)] = 1
    for nn in range(1, n):
        ser_[ser > np.nanquantile(ser, nn / n)] = nn + 1
    return ser_


def value_line(r):
    '''
    转化日收益率为净值曲线/累计收益
    :param r: DataFrame
    :return: 净值曲线/累计收益
    '''
    value = r.copy()
    r_ = r.copy()
    r_[np.isnan(r_)] = 0
    for i in range(r.shape[0]):
        if i == 0:
            value[i, :] = 1
        else:
            value[i, :] = value[i - 1, :] * (1 + r_[i, :] / 100)
    return value


def calc_decay(F, R):
    '''
    计算因子衰减率，即Corr(Ft, Rt+1+n)
    :param F: 因子
    :param R: 收益率
    :return:
    '''
    start = time.time()
    print('开始计算因子衰减率...')
    decay_period = [1, 2, 3, 5, 8, 13, 21, 34, 55]
    IC_decay = np.full((len(decay_period), R.shape[1]), np.nan)
    # 空值赋成列平均值
    F_ = F.apply(fill_by_mean, axis=0)
    R_ = R.apply(fill_by_mean, axis=0)
    for i in range(len(decay_period)):
        Ft = F_.iloc[:-decay_period[i], :]
        Rt = R_.iloc[decay_period[i]:, :]
        for j in range(R.shape[1]):
            Ftj = Ft.iloc[:, j]
            Rtj = Rt.iloc[:, j]
            FRnotnull = np.where(~np.isnan(np.vstack([Ftj, Rtj]).sum(axis=0)))
            if len(FRnotnull[0]) <= 1:
                continue
            Ftj = Ftj.iloc[FRnotnull]
            Rtj = Rtj.iloc[FRnotnull]
            IC_decay[i, j] = np.corrcoef(Ftj, Rtj)[0, 1]

    IC_decay_ = np.nanmean(IC_decay, axis=1)
    end = time.time()
    print(f'因子衰减率计算完毕，用时{end - start}s')
    return IC_decay_


def figures(data1, data2, data3, data4, data5, data6, fontsize=6):
    # 对回测结果作图：1-多空收益曲线 2-五组收益曲线 3-因子单调性 4-因子最后一个截面的分布 5-因子衰减率 6-行业分布
    plt.rcParams.update({'font.size': fontsize})

    fig, axes = plt.subplots(2, 3)
    axes[0, 0].plot(data1, label=data1.columns)
    axes[0, 0].xaxis.set_major_locator(mticker.FixedLocator(
        np.arange(1, data1.shape[0], int(data1.shape[0]/10))))  # 定位到x轴
    axes[0, 0].set_xticklabels([data1.index[i] for i in range(0, data1.shape[0]+1, int(data1.shape[0]/10))],
                               rotation=30, fontsize=5)
    axes[0, 0].xaxis.set_ticks_position('top')
    axes[0, 0].set_title('Long short returns')
    axes[0, 0].legend()

    axes[0, 1].plot(data2, label=data2.columns)
    axes[0, 1].xaxis.set_major_locator(mticker.FixedLocator(
        np.arange(1, data2.shape[0], int(data2.shape[0] / 10))))  # 定位到x轴
    axes[0, 1].set_xticklabels([data2.index[i] for i in range(0, data2.shape[0] + 1, int(data2.shape[0] / 10))],
                               rotation=30, fontsize=5)
    axes[0, 1].xaxis.set_ticks_position('top')
    axes[0, 1].set_title('Returns')
    axes[0, 1].legend()

    axes[0, 2].bar(np.linspace(1, data3.shape[0], data3.shape[0]), data3)
    axes[0, 2].xaxis.set_ticks_position('top')
    axes[0, 2].set_title('Monotonicity')

    axes[1, 0].bar(['1', '2', '3', '5', '8', '13', '21', '34', '55'], data4)
    axes[1, 0].set_title('Decay rate')

    axes[1, 1].hist(data5, bins=100, range=(data5.min(), data5.max()))
    axes[1, 1].set(xlim=(data5.min(), data5.max()))
    axes[1, 1].set_title('Factor distribution')

    axes[1, 2].bar(np.linspace(1, data6.shape[0], data6.shape[0]), data6)
    axes[1, 2].xaxis.set_major_locator(mticker.FixedLocator(np.linspace(1, data6.shape[0], data6.shape[0])))  # 定位到x轴
    axes[1, 2].set_xticklabels(industry.columns, rotation=80, font='SimHei', fontsize=4)
    axes[1, 2].set_title('Industry distribution')

    plt.show()


# 读取回测必要数据
# 行业分类
industry = pd.read_csv('.\\Data\\Industry.csv',
                           encoding='GBK', index_col='Unnamed: 0')['中信行业\n1级']
industry = onehot(industry, '中信行业\n1级')

# 股票收益率
stockrate = pd.read_csv('.\\Data\\stockrate.csv', encoding='GBK',
                      index_col='Unnamed: 0', parse_dates=['Unnamed: 0'])

