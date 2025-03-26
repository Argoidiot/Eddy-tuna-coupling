#! /usr/bin/env/python3
# -*- coding=utf-8 -*-
"""
======================模块功能描述=========================    
       @File     : 涡-鱼匹配折线图(2010~2021).py
       @IDE      : PyCharm
       @Author   : Wukkkkk
       @Date     : 2024/7/13 上午10:09
       @Desc     : 涡-鱼匹配折线图绘制(2010~2021)
=========================================================   
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as mticker
from matplotlib.ticker import ScalarFormatter
plt.rcParams['font.sans-serif'] = ['Arial']

def export_legend(legend, filename="legend.png", expand=[-5, -5, 5, 5]):
    # 创建一个新的图形和坐标轴
    fig_legend = plt.figure(figsize=(10, 2), dpi=150)  # 设置图例图像的大小
    ax_legend = fig_legend.add_axes([0, 0, 1, 1])  # 添加坐标轴
    ax_legend.axis('off')  # 隐藏坐标轴

    # 将图例复制到新图中
    ax_legend.legend(*ax.get_legend_handles_labels(), frameon=True, fontsize=36, ncol=2)

    # 调整布局并保存
    fig_legend.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close(fig_legend)


file = r'G:\科研\论文绘图\渔获量系数(2010~2021) .xlsx'
data = pd.read_excel(file)
df = data.iloc[1:, 1:-2]
kArraySkj = df.iloc[0].tolist()
# kArrayBet = df.iloc[1].tolist()
kArrayBet = [0.0000557, 0.0001324, 0.0001040, 0.0001217, 0.0000910, 0.0001345, 0.0001408, 0.0000926, 0.0000808]
kArrayYft = df.iloc[2].tolist()

fig = plt.figure(figsize=(12, 8), dpi=150)

ax = fig.add_subplot(111)
yArrayAE = [i for i in kArrayYft[0:4] for _ in range(2)]
yArrayCE = [i for i in kArrayYft[4:8] for _ in range(2)]

xtick = [0, 0.5, 0.5, 1, 1, 1.5, 1.5, 2, ]
ax.plot(xtick, yArrayAE, c='#740000', label='AE', lw=2.55)
ax.plot(xtick, yArrayCE, c='#000074', label='CE', lw=2.55)
# ax.axhline(y=kArrayYft[-1], ls='--', c='gray', alpha=0.5)  # 涡外的值
xtickLabel = ['0', '0.5', '1', '1.5', '2']
ax.set_xticks(np.arange(0, 2.0001, 0.5), xtickLabel)
ax.set_xlim(0, 2)
ax.tick_params(axis='both', which='major', labelsize=30, length=8, width=2.5)
ax.tick_params(axis='both', which='minor', labelsize=30, length=5, width=2.5)
format_ = ScalarFormatter(useMathText=True)
format_.set_scientific(True)
format_.set_powerlimits((-3, 4))
ax.yaxis.set_major_formatter(format_)
offset_text = ax.yaxis.get_offset_text()
# 设置标记的字体大小
offset_text.set_fontsize(25)
for spine in ax.spines.values():
    spine.set_linewidth(2.5)

ax.xaxis.set_minor_locator(mticker.MultipleLocator(1))
ax.yaxis.set_minor_locator(mticker.MultipleLocator(400))
ax.set_xlabel('Normalized distance (r/R)', fontsize=36)
ax.set_ylabel('k(t/km²)', fontsize=36)
legend =ax.legend(frameon=True, fontsize=36, ncol=2)
ax.text(1.72, 0.0001530, s='YFT', fontsize=40, color='k', weight='normal')
# ax.text(0.02, 0.0000440, s='(b)', fontsize=48, color='k', weight='normal')
# 调用函数导出图例
export_legend(legend, filename="legend.png")
# plt.savefig(r'G:\学习\小论文\图片\Yft折线图（2010~2021）.png', dpi=150, bbox_inches='tight')
# plt.show()