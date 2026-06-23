# -*- coding: utf-8 -*-
"""
应用量化分析 - 作业3
任务：在模型中加入调节变量，进行回归估计并绘制调节效应图
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

# 设置 matplotlib 画图时的中文支持 (macOS 常用中文字体)
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'Songti SC', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 1. 导入数据 (CFPS 2022 个人库)
print("正在读取数据...")
file_path = "示例数据与代码/cfps2022person_202410.dta"
needed_cols = [
    'qn12012', 'qu201', 'qu201a', 'qu202', 'qu202a', 
    'age', 'gender', 'cfps2022eduy', 'qea0', 'qp201', 'emp_income', 'urban22'
]
df = pd.read_stata(file_path, columns=needed_cols)

# 2. 变量清洗与处理
print("正在清理变量...")

# 被解释变量：生活满意度 (1到5分)
df['satisfaction'] = pd.to_numeric(df['qn12012'], errors='coerce')
df.loc[~df['satisfaction'].isin([1, 2, 3, 4, 5]), 'satisfaction'] = np.nan

# 核心解释变量：每日上网时长 (手机 + 电脑，换算为小时)
df['mobile_time'] = pd.to_numeric(df['qu201a'], errors='coerce').fillna(0)
df['pc_time'] = pd.to_numeric(df['qu202a'], errors='coerce').fillna(0)
df.loc[df['qu201'].isin(['否', '不适用']), 'mobile_time'] = 0
df.loc[df['qu202'].isin(['否', '不适用']), 'pc_time'] = 0
df['net_hours'] = (df['mobile_time'] + df['pc_time']) / 60.0
df.loc[df['net_hours'] > 24, 'net_hours'] = np.nan

# 调节变量：年龄 (周岁)
df['age'] = pd.to_numeric(df['age'], errors='coerce')

# 控制变量：性别 (男=1, 女=0)
df['is_male'] = (df['gender'] == '男').astype(float)
df.loc[df['gender'].isna(), 'is_male'] = np.nan

# 控制变量：受教育年限
df['edu'] = pd.to_numeric(df['cfps2022eduy'], errors='coerce')

# 控制变量：婚姻状况 (在婚=1, 其他=0)
df['is_married'] = (df['qea0'] == '在婚（有配偶）').astype(float)
df.loc[df['qea0'].isna() | (df['qea0'] == '没有有效数据'), 'is_married'] = np.nan

# 控制变量：健康状况 (映射为1-5分)
health_dict = {'不健康': 1, '一般': 2, '比较健康': 3, '很健康': 4, '非常健康': 5}
df['health'] = df['qp201'].map(health_dict).astype(float)

# 控制变量：个人年收入 (取对数)
df['income'] = pd.to_numeric(df['emp_income'], errors='coerce').fillna(0)
df['log_income'] = np.log1p(df['income'])

# 控制变量：城乡属性 (城镇=1, 农村=0)
df['is_urban'] = (df['urban22'] == '城镇').astype(float)

# 保留分析所需的完整样本
analysis_vars = ['satisfaction', 'net_hours', 'age', 'is_male', 'edu', 'is_married', 'health', 'log_income', 'is_urban']
data = df[analysis_vars].dropna().copy()
print(f"数据清洗完毕，有效样本量为: {len(data)}")

# 3. 描述性统计
print("\n================= 表1：主要变量的描述性统计 =================")
desc = data.describe().T[['count', 'mean', 'std', 'min', 'max']]
desc.columns = ['样本量', '均值', '标准差', '最小值', '最大值']
print(desc.round(2))

# 4. 相关系数矩阵
print("\n================= 表2：变量间 Pearson 相关系数 =================")
corr_matrix = data.corr().round(2)
print(corr_matrix)

# 5. 多重线性回归估计 (使用异方差稳健标准误 HC1)
print("\n================= 表3：回归模型估计结果 =================")

# 模型1：基准模型 (只包含控制变量)
m1_formula = "satisfaction ~ age + is_male + edu + is_married + health + log_income + is_urban"
model1 = smf.ols(m1_formula, data=data).fit(cov_type='HC1')
print("\n--- 模型 1 (仅包含控制变量) ---")
print(model1.summary())

# 模型2：主效应模型 (加入上网时长)
m2_formula = "satisfaction ~ net_hours + age + is_male + edu + is_married + health + log_income + is_urban"
model2 = smf.ols(m2_formula, data=data).fit(cov_type='HC1')
print("\n--- 模型 2 (主效应模型) ---")
print(model2.summary())

# 模型3：调节效应模型 (加入交互项 net_hours * age)
m3_formula = "satisfaction ~ net_hours * age + is_male + edu + is_married + health + log_income + is_urban"
model3 = smf.ols(m3_formula, data=data).fit(cov_type='HC1')
print("\n--- 模型 3 (加入年龄调节效应) ---")
print(model3.summary())

# 6. 绘制调节效应图
print("\n正在绘制调节效应图...")
plt.figure(figsize=(7, 4.5))

# 设定上网时间范围从 0 到 10 小时
x_net = np.linspace(0, 10, 100)

# 其他控制变量取均值
mean_controls = {v: data[v].mean() for v in ['is_male', 'edu', 'is_married', 'health', 'log_income', 'is_urban']}

# 模型3回归参数
params = model3.params
ctrl_contrib = sum(params[v] * mean_controls[v] for v in mean_controls)

# 计算三个代表性年龄组（青年 20岁，中年 45岁，老年 70岁）的预测曲线
y_20 = params['Intercept'] + params['net_hours'] * x_net + params['age'] * 20 + params['net_hours:age'] * x_net * 20 + ctrl_contrib
y_45 = params['Intercept'] + params['net_hours'] * x_net + params['age'] * 45 + params['net_hours:age'] * x_net * 45 + ctrl_contrib
y_70 = params['Intercept'] + params['net_hours'] * x_net + params['age'] * 70 + params['net_hours:age'] * x_net * 70 + ctrl_contrib

# 绘图曲线
plt.plot(x_net, y_20, label='青年 (20岁)', color='#1f77b4', linewidth=2, linestyle='-')
plt.plot(x_net, y_45, label='中年 (45岁)', color='#2ca02c', linewidth=2, linestyle='--')
plt.plot(x_net, y_70, label='老年 (70岁)', color='#d62728', linewidth=2, linestyle='-.')

plt.title('年龄对“上网时长 -> 生活满意度”关系的调节效应图', fontsize=12, pad=15)
plt.xlabel('每日上网时间 (小时)', fontsize=10)
plt.ylabel('生活满意度预测值 (1-5分)', fontsize=10)
plt.xlim(0, 10)
plt.ylim(3.5, 4.5)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.tight_layout()

# 保存图像
plt.savefig("moderation_effect.png", dpi=300)
print("调节效应图已成功绘制并保存为 'moderation_effect.png'。")
