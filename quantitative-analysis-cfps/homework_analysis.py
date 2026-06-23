import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings('ignore')

# 1. 读取数据
file_path = "示例数据与代码/cfps2022person_202410.dta"
print("正在读取数据...")
needed_cols = [
    'qn12012', 'qu201', 'qu201a', 'qu202', 'qu202a', 
    'age', 'gender', 'cfps2022eduy', 'qea0', 'qp201', 'emp_income', 'urban22'
]
df = pd.read_stata(file_path, columns=needed_cols)

# 2. 数据清洗和变量构造
# 生活满意度 (1到5分)
df['satisfaction'] = pd.to_numeric(df['qn12012'], errors='coerce')
df.loc[~df['satisfaction'].isin([1, 2, 3, 4, 5]), 'satisfaction'] = np.nan

# 计算上网时长 (手机 + 电脑)
df['mobile_time'] = pd.to_numeric(df['qu201a'], errors='coerce').fillna(0)
df['pc_time'] = pd.to_numeric(df['qu202a'], errors='coerce').fillna(0)

# 处理没上网的情况
df.loc[df['qu201'].isin(['否', '不适用']), 'mobile_time'] = 0
df.loc[df['qu202'].isin(['否', '不适用']), 'pc_time'] = 0

# 换算成小时
df['net_hours'] = (df['mobile_time'] + df['pc_time']) / 60.0
df.loc[df['net_hours'] > 24, 'net_hours'] = np.nan

# 控制变量处理
df['age'] = pd.to_numeric(df['age'], errors='coerce')

df['is_male'] = (df['gender'] == '男').astype(float)
df.loc[df['gender'].isna(), 'is_male'] = np.nan

df['edu'] = pd.to_numeric(df['cfps2022eduy'], errors='coerce')

df['is_married'] = (df['qea0'] == '在婚（有配偶）').astype(float)
df.loc[df['qea0'].isna() | (df['qea0'] == '没有有效数据'), 'is_married'] = np.nan

# 健康状况映射
health_dict = {'不健康': 1, '一般': 2, '比较健康': 3, '很健康': 4, '非常健康': 5}
df['health'] = df['qp201'].map(health_dict).astype(float)

# 收入取对数
df['income'] = pd.to_numeric(df['emp_income'], errors='coerce').fillna(0)
df['log_income'] = np.log1p(df['income'])

df['is_urban'] = (df['urban22'] == '城镇').astype(float)

# 删除缺失值保留有效样本
analysis_vars = ['satisfaction', 'net_hours', 'age', 'is_male', 'edu', 'is_married', 'health', 'log_income', 'is_urban']
data = df[analysis_vars].dropna().copy()
print(f"数据清洗完毕，有效样本量: {len(data)}\n")

# 3. 描述性统计
print("================= 1. 描述性统计 =================")
desc = data.describe().T[['count', 'mean', 'std', 'min', 'max']]
desc.columns = ['样本量', '均值', '标准差', '最小值', '最大值']
print(desc.round(2))
print("\n")

# 4. 相关性分析
print("================= 2. 相关系数矩阵 ==================")
corr_matrix = data.corr().round(2)
print(corr_matrix)
print("\n")

# 5. 回归模型
print("================= 3. 回归分析结果 ==================")
# 基准模型：只包含控制变量
m1_formula = "satisfaction ~ age + is_male + edu + is_married + health + log_income + is_urban"
model1 = smf.ols(m1_formula, data=data).fit(cov_type='HC1')
print("--- 模型1 (基准模型) ---")
print(model1.summary())
print("\n")

# 主模型：加入上网时长
m2_formula = "satisfaction ~ net_hours + age + is_male + edu + is_married + health + log_income + is_urban"
model2 = smf.ols(m2_formula, data=data).fit(cov_type='HC1')
print("--- 模型2 (加入主效应) ---")
print(model2.summary())
