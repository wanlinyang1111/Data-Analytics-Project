import numpy as np
import pandas as pd
import pymysql
from sqlalchemy import create_engine, inspect, text
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter

import re

# Energy Supply Yearly Data 
ALL_E_G = pd.read_csv("經濟部能源署_能源供給年資料.csv")
ALL_E_G.info()

# Set the column "日期(年)" as the new index
ALL_E_G = ALL_E_G.set_index('日期(年)')

# Keep only the columns for the aggregated quantities of the five major categories
columns_to_keep = ['能源總供給_煤及煤產品', '能源總供給_原油及石油產品', '能源總供給_天然氣', '能源總供給_核能', '能源總供給_再生能源_小計']
ALL_E_G = ALL_E_G[columns_to_keep]

ALL_E_G.to_csv("ALL_E_G.csv")

#%%

# Yearly Data on Renewable Energy Generation 
y_RE_G = pd.read_csv("經濟部能源署_再生能源發電量年資料.csv")
y_RE_G.info()

# Set the column "日期(年)" as the new index
y_RE_G = y_RE_G.set_index('日期(年)')

# Delete the calculated data columns
columns_to_drop = ["風力_陸域", "風力_離岸","生質能_固態","生質能_氣態"]
y_RE_G.drop(columns=columns_to_drop, inplace=True)

y_RE_G.to_csv("y_RE_G.csv")

#%%

# Yearly Data on Installed Capacity of Renewable Energy
y_IC_RE = pd.read_csv("經濟部能源署_再生能源裝置容量年資料.csv")
y_IC_RE.info()

# set column"日期(年)" as the new index
y_IC_RE = y_IC_RE.set_index('日期(年)')

# Delete the calculated data columns
columns_to_drop = ["再生能源發電裝置_風力_陸域", "再生能源發電裝置_風力_離岸","再生能源發電裝置_生質能_固態","再生能源發電裝置_生質能_氣態","再生能源裝設容量_太陽能熱水器裝設面積(千平方公尺)"]
y_IC_RE.drop(columns = columns_to_drop, inplace = True)

y_IC_RE.to_csv("y_IC_RE.csv")

#%%

# Solor Photovoltaic (SP)
SP = pd.read_csv("光電發電.csv")
SP.info()

# Due to the excessive length of the column names, they cannot be stored in the database. Therefore, English characters need to be removed.
# Define a function to remove non-Chinese characters
def keep_chinese_characters(column_name):
    # Use regular expressions to find all Chinese characters (\u4e00-\u9fff represents the range of Chinese characters in Unicode)
    chinese_characters = re.findall(r'[\u4e00-\u9fff]', column_name)
    return ''.join(chinese_characters)

# Apply this function to every column name in the DataFrame using the map method
SP.columns = SP.columns.map(keep_chinese_characters)

# group by year and count the sum
SP_y = SP.groupby("年度").sum()

# Delete the columns don't need
columns_to_drop = ["月份","日期","每日發電量度"]
SP_y.drop(columns=columns_to_drop, inplace=True)

# When creating visualizations, it was challenging to represent the data, so I manually added the corresponding city names to all columns
SP_y.columns = ["金門-金門金沙光電","台中-台中電廠光電","高雄-興達電廠光電","嘉義-嘉義民雄光電","台中-中部儲運中心光電","台中-東勢新伯公光電","高雄-永安鹽灘地光電","高雄-路北光電","澎湖-澎湖尖山光電","桃園-中大光電","苗栗-卓蘭會館光電","桃園-大潭電廠光電","澎湖-澎湖七美光電","屏東-核三廠光電","台中-后里光電","台中-台中龍井光電","桃園-龍潭光電","新竹-竹工光電","台中-中科光電","彰化-彰林光電","台南-台南七股光電","高雄-高雄光電","高雄-燕巢倉庫光電","桃園-北部儲運中心光電","彰化-彰化彰濱光電","台南-台南鹽田光電","南投-南投大彎光電","金門-金門鵲山光電","金門-金門塔山光電","高雄-高雄保寧光電","馬祖-馬祖珠山光電","蘭嶼-蘭嶼貯存場光電","蘭嶼-蘭嶼電廠光電","桃園-大湳淨水場光電","桃園-平鎮淨水場光電","苗栗-東興淨水場光電","桃園-龍潭淨水場光電","桃園-龜山加壓站光電","新北-淡水萬噸配水池光電","高雄-鳳山水庫光電","嘉義-義竹工作站光電","嘉義-嘉義分所光電"]

# Transpose the data for easier visualization charting later on
SP_y=SP_y.T

# Store the original index as a column, and modify the column name
SP_y.reset_index(inplace=True)
SP_y.rename(columns={'index': '光電站名稱'}, inplace=True)

# Create a separate column for 所屬縣市， then delete the columns don't need
SP_y["所屬縣市"] = SP_y["光電站名稱"].str.slice(0, 2)
SP_y = SP_y.drop(columns=["光電站名稱"])

# group by 所屬縣市 and count the sum
SP_y = SP_y.groupby("所屬縣市").sum()

SP_y.to_csv("SP_y.csv")

#%%

# Taiwan Power Company (TPC) pruchased Solor Photovoltaic (SP)
TPC_pruchased_SP = pd.read_csv("台灣電力公司_太陽光電購電實績.csv")
TPC_pruchased_SP.info()

# set column 年度：民國 to 西元
TPC_pruchased_SP["年度"] = TPC_pruchased_SP["年度"]+1911

# delete first 4 rows because no month's data
TPC_pruchased_SP = TPC_pruchased_SP.drop([0,1,2,3])

# group by year and count the sum
TPC_pruchased_SP = TPC_pruchased_SP.groupby("年度")["度數(千度)"].sum().to_frame()

TPC_pruchased_SP.to_csv("TPC_pruchased_SP.csv")

#%%

# wind power (WP)
WP = pd.read_csv("風力發電.csv")
WP.info()

# Define a function to remove non-Chinese characters
def keep_chinese_characters(column_name):
    # Use regular expressions to find all Chinese characters (\u4e00-\u9fff represents the range of Chinese characters in Unicode)
    chinese_characters = re.findall(r'[\u4e00-\u9fff]', column_name)
    return ''.join(chinese_characters)

# Apply this function to every column name in the DataFrame using the map method
WP.columns = WP.columns.map(keep_chinese_characters)

WP = WP.replace(',', '', regex=True)
WP = WP.apply(pd.to_numeric, errors='coerce', downcast='integer')

WP.info()

# group by year and count the sum
WP_y = WP.groupby("年度").sum()

# Delete the columns don't need
columns_to_drop = ["月份","日期","每日發電量度"]
WP_y.drop(columns=columns_to_drop, inplace=True)

# When creating visualizations, it was challenging to represent the data, so I manually added the corresponding city names to all columns
WP_y.columns = ["新北-石門風電","新北-林口風電","桃園-蘆竹風電","桃園-觀園風電","桃園-大潭風電","新竹-香山風電","台中-台中港區風電","台中-電廠風電","彰化-彰工風電","彰化-彰化王功風電","彰化-彰化永興風電","雲林-雲林麥寮風電","雲林-雲林四湖風電","屏東-恆春風電","台中-中屯風電","澎湖-湖西風電","金門-金沙風電","澎湖-龍門風電"]

# Transpose the data for easier visualization charting later on
WP_y=WP_y.T

# Store the original index as a column, and modify the column name
WP_y.reset_index(inplace=True)
WP_y.rename(columns={'index': '風電站名稱'}, inplace=True)

# Create a separate column for 所屬縣市， then delete the columns don't need
WP_y["所屬縣市"] = WP_y["風電站名稱"].str.slice(0, 2)
WP_y = WP_y.drop(columns=["風電站名稱"])

# group by 所屬縣市 and count the sum
WP_y = WP_y.groupby("所屬縣市").sum()

WP_y.to_csv("WP_y.csv")


#%%

# Statistics on Investment by Overseas Chinese and Foreigners in Taiwan by Industry
Inv_TW_indus_OCandF = pd.read_csv("華僑及外國人來來臺投資分業資料統計.csv")
Inv_TW_indus_OCandF.info()

# delete NaN
Inv_TW_indus_OCandF.dropna(inplace = True)

# delete data befor 民國91年 because others dataset begin nearly 民國90年
np.where(Inv_TW_indus_OCandF.eq(9101))
Inv_TW_indus_OCandF.drop(index=range(0, 7726), inplace = True)

# Split the "Approval Year-Month" column into "Year" and "Month"
Inv_TW_indus_OCandF["核准年月"] = Inv_TW_indus_OCandF["核准年月"].astype(str)
Inv_TW_indus_OCandF["核准年"] = Inv_TW_indus_OCandF["核准年月"].str.slice(0, -2).astype(int)     
Inv_TW_indus_OCandF["核准月"] = Inv_TW_indus_OCandF["核准年月"].str.slice(-2, None).astype(int)  

# set column 核准月：民國 to 西元
Inv_TW_indus_OCandF["核准年"] = Inv_TW_indus_OCandF["核准年"]+1911

# drop the column don't need
Inv_TW_indus_OCandF.drop(columns = ["核准年月","行業代碼"], inplace = True)

# count the number of approvals each year
Inv_TW_indus_OCandF_num_by_y = Inv_TW_indus_OCandF.groupby("核准年")["件數"].sum().to_frame().sort_values(by = "核准年",ascending = True)
Inv_TW_indus_OCandF_num_by_y.to_csv("Inv_TW_indus_OCandF_num_by_y.csv")

# Find the number of approvals and the total investment amount related to "電力|發電" each year
indus=Inv_TW_indus_OCandF.loc[:,"行業名稱"].unique()
contains_electric = Inv_TW_indus_OCandF[Inv_TW_indus_OCandF['行業名稱'].str.contains("電力|發電")]
Inv_TW_indus_OCandF_by_e_num_by_y = contains_electric.groupby("核准年")["件數"].sum().to_frame().sort_values(by = "核准年",ascending = True)
Inv_TW_indus_OCandF_by_e_im_by_y = contains_electric.groupby("核准年")["金額-千美元"].sum().to_frame().sort_values(by = "核准年",ascending = True)

Inv_TW_indus_OCandF_by_e_num_by_y.to_csv("Inv_TW_indus_OCandF_by_e_num_by_y.csv")
Inv_TW_indus_OCandF_by_e_im_by_y.to_csv("Inv_TW_indus_OCandF_by_e_im_by_y.csv")


#%%

# 先手動開啟heidiSQL，並手動創建資料庫"renewable_energy_analysis"
# 連到MySQL

# 資料庫連接參數
MYSQL_HOST = "localhost"
MYSQL_DB = "renewable_energy_analysis"
MYSQL_USER = "root"
MYSQL_PASS = "aaaaa"

def connect_mysql():
    global connect, cursor
    connect = pymysql.connect(host=MYSQL_HOST,
                              db=MYSQL_DB,
                              user=MYSQL_USER,
                              password=MYSQL_PASS,
                              charset="utf8",
                              use_unicode=True)
    cursor = connect.cursor()

connect_mysql()

# 連接到資料庫
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}/{MYSQL_DB}")

# 定義函數檢查表格是否存在
def table_exists(engine, table_name):
    inspector = inspect(engine)
    return inspector.has_table(table_name) #會回傳bool值

# 將資料存到MySQL資料庫中
table_names = ["ALL_E_G","y_RE_G","SP_y","WP_y","TPC_pruchased_SP","y_IC_RE","Inv_TW_indus_OCandF_num_by_y","Inv_TW_indus_OCandF_by_e_num_by_y","Inv_TW_indus_OCandF_by_e_im_by_y"]

for table in table_names:
    data = pd.read_csv(table+".csv")

    if table_exists(engine, table):
        print(f"Table {table} already exists. Dropping and recreating it.")
        with engine.connect() as con:
            con.execute(text(f"DROP TABLE IF EXISTS {table}"))

    data.to_sql(table, con=engine, if_exists='replace', index=False)
    table = pd.read_sql(f"SELECT * FROM {table}", con=engine)

#%%

# 📊從資料庫讀取資料，並製作視覺化圖表📊

#%%

# 📍經濟部能源署_能源供給年資料.csv
# 折線圖(全部)
ALL_E_G = pd.read_sql("SELECT * FROM ALL_E_G", con = connect)

plt.rcParams["font.family"] = "Microsoft JhengHei"
plt.rcParams["font.size"] = 15
plt.rcParams["axes.unicode_minus"] = False

x = ALL_E_G ["日期(年)"]
y1 = ALL_E_G ["能源總供給_煤及煤產品"]
y2 = ALL_E_G ["能源總供給_原油及石油產品"]
y3 = ALL_E_G ["能源總供給_天然氣"]
y4 = ALL_E_G ["能源總供給_核能"]
y5 = ALL_E_G ["能源總供給_再生能源_小計"]

plt.figure(figsize=(13,8))

plt.plot(x,y1, label="煤及煤產品")
plt.plot(x,y2, label="原油及石油產品")
plt.plot(x,y3, label="天然氣")
plt.plot(x,y4, label="核能")
plt.plot(x,y5, label="再生能源")

x_major_locator = MultipleLocator(2)
ax = plt.gca()
ax.xaxis.set_major_locator(x_major_locator)

plt.title("能源供給量(2002年-2022年)")
plt.xlabel("西元年份")
plt.ylabel("千公秉油當量")
plt.legend(title="圖例",loc='upper left', bbox_to_anchor=(1, 1),frameon=False)
plt.tight_layout()  # 自動調整圖表佈局
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
# 添加網格線
ax.grid(True, linestyle='--', alpha=0.7)
plt.show()



#2002年和2022年能源供給結構對比
#圓餅圖
eg_type= ['煤及煤產品', '原油及石油產品', '天然氣', '核能', '再生能源']
eg_2002=ALL_E_G.iloc[0,1:]
eg_2022=ALL_E_G.iloc[20,1:]
exp=[0,0,0,0,0.5]

plt.figure(figsize=(15,8))

plt.title("2002年能源供給結構")
plt.pie(eg_2002, labels=eg_type, autopct="%d%%", explode=exp, shadow=True, pctdistance=0.8)
plt.show()

plt.figure(figsize=(15,8))

plt.title("2022年能源供給結構")
plt.pie(eg_2022, labels=eg_type, autopct="%d%%", explode=exp, shadow=True, pctdistance=0.8)
plt.show()

#%%

# 📍經濟部能源署_再生能源發電量年資料.csv
# 折線圖
y_RE_G = pd.read_sql("SELECT * FROM y_RE_G", con = connect)

plt.rcParams["font.family"] = "Microsoft JhengHei"
plt.rcParams["font.size"] = 15
plt.rcParams["axes.unicode_minus"] = False

x = y_RE_G ["日期(年)"]
y1 = y_RE_G ["慣常水力"]
y2 = y_RE_G ["地熱"]
y3 = y_RE_G ["太陽光電"]
y4 = y_RE_G ["風力_小計"]
y5 = y_RE_G ["生質能_小計"]
y6 = y_RE_G ["廢棄物"]

plt.figure(figsize=(13,8))

plt.plot(x,y1, label="慣常水力")
plt.plot(x,y2, label="地熱")
plt.plot(x,y3, label="太陽光電")
plt.plot(x,y4, label="風力")
plt.plot(x,y5, label="生質能")
plt.plot(x,y6, label="廢棄物")

x_major_locator = MultipleLocator(2)
ax = plt.gca()
ax.xaxis.set_major_locator(x_major_locator)

plt.title("再生能源發電量(2002年-2022年)", fontsize=30)
plt.xlabel("西元年份")
plt.ylabel("千度")
plt.legend(title="圖例",loc='upper left', bbox_to_anchor=(1, 1),frameon=False)
plt.tight_layout()  # 自動調整圖表佈局
ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=False))
ax.yaxis.get_major_formatter().set_scientific(False)
ax.yaxis.get_major_formatter().set_useOffset(False)
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
# 添加網格線
ax.grid(True, linestyle='--', alpha=0.7)
plt.show()

#%%

# 📍經濟部能源署_再生能源裝置容量年資料.csv
# 折線圖
y_IC_RE = pd.read_sql("SELECT * FROM y_IC_RE", con = connect)

plt.rcParams["font.family"] = "Microsoft JhengHei"
plt.rcParams["font.size"] = 15
plt.rcParams["axes.unicode_minus"] = False

x = y_IC_RE["日期(年)"]
y1 = y_IC_RE ["再生能源發電裝置_慣常水力"]
y2 = y_IC_RE ["再生能源發電裝置_地熱"]
y3 = y_IC_RE ["再生能源發電裝置_太陽光電"]
y4 = y_IC_RE ["再生能源發電裝置_風力_小計"]
y5 = y_IC_RE ["再生能源發電裝置_生質能_小計"]
y6 = y_IC_RE ["再生能源發電裝置_廢棄物"]

plt.figure(figsize=(13,8))

plt.plot(x,y1, label="慣常水力")
plt.plot(x,y2, label="地熱")
plt.plot(x,y3, label="太陽光電")
plt.plot(x,y4, label="風力")
plt.plot(x,y5, label="生質能")
plt.plot(x,y6, label="廢棄物")

x_major_locator = MultipleLocator(2)
ax = plt.gca()
ax.xaxis.set_major_locator(x_major_locator)

plt.title("再生能源裝置容量(2002年-2022年)", fontsize=30)
plt.xlabel("西元年份")
plt.ylabel("千瓩")
plt.legend(title="圖例",loc='upper left', bbox_to_anchor=(1, 1),frameon=False)
plt.tight_layout()  # 自動調整圖表佈局
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
# 添加網格線
ax.grid(True, linestyle='--', alpha=0.7)
plt.show()

#%%

#📍光電發電.csv

SP_y = pd.read_sql("SELECT * FROM SP_Y", con = connect)

# 將索引設置為'所屬縣市'，這樣每一行都會表示一個城市
SP_y.set_index('所屬縣市', inplace=True)

# 繪製熱力圖
plt.figure(figsize=(14, 8))
plt.title('台灣電力公司_各城市各年份太陽光電發電量')
plt.imshow(SP_y, aspect='auto', cmap='coolwarm')
SP_y.info()
plt.colorbar(label='發電量(度)')
plt.xticks(range(len(SP_y.columns)), SP_y.columns, rotation=45)
plt.yticks(range(len(SP_y.index)), SP_y.index)
plt.xlabel('年份')
plt.ylabel('城市')
plt.show()

# 📍台灣電力公司_太陽光電購電實績.csv
# 長條圖
TPC_pruchased_SP = pd.read_sql("SELECT * FROM TPC_pruchased_SP", con = connect)

years = TPC_pruchased_SP["年度"]
values = TPC_pruchased_SP["度數(千度)"]

fig, ax = plt.subplots(figsize=(13, 8))

ax.bar(years, values, color='skyblue')

# 設置標題和軸標籤
ax.set_title('台灣電力公司-太陽光電購電實績', fontsize=16)
ax.set_xlabel('年份', fontsize=14)
ax.set_ylabel('購電量 (千萬)', fontsize=14)

# 設置Y軸的格式化方式，避免科學記數法
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

# 設置X軸刻度顯示的格式
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:.0f}'.format(x)))

# 添加網格線
ax.grid(True, linestyle='--', alpha=0.7)

# 調整刻度字體大小
ax.tick_params(axis='both', which='major', labelsize=12)

plt.tight_layout()
plt.show()

#%%

#📍風力發電.csv

WP_y = pd.read_sql("SELECT * FROM WP_y", con = connect)

# 將索引設置為'所屬縣市'，這樣每一行都會表示一個城市
WP_y.set_index('所屬縣市', inplace=True)

# 繪製熱力圖
plt.figure(figsize=(14, 8))
plt.title('台灣電力公司_各城市各年份風力發電發電量')
plt.imshow(WP_y, aspect='auto', cmap='coolwarm')
WP_y.info()
plt.colorbar(label='發電量(度)')
plt.xticks(range(len(WP_y.columns)), WP_y.columns, rotation=45)
plt.yticks(range(len(WP_y.index)), WP_y.index)
plt.xlabel('年份')
plt.ylabel('城市')
plt.show()
    
#%%
# 📍華僑及外國人來臺投資分業資料統計.csv

Inv_TW_indus_OCandF_num_by_y = pd.read_sql("SELECT * FROM Inv_TW_indus_OCandF_num_by_y", con = connect)
Inv_TW_indus_OCandF_by_e_num_by_y = pd.read_sql("SELECT * FROM Inv_TW_indus_OCandF_by_e_num_by_y", con = connect)
Inv_TW_indus_OCandF_by_e_im_by_y = pd.read_sql("SELECT * FROM Inv_TW_indus_OCandF_by_e_im_by_y", con = connect)

# 使用SQL LEFT JOIN語法    
query = """
SELECT inv_tw_indus_ocandf_by_e_num_by_y.核准年, 
       inv_tw_indus_ocandf_by_e_num_by_y.件數, 
       inv_tw_indus_ocandf_by_e_im_by_y.`金額-千美元`
FROM inv_tw_indus_ocandf_by_e_num_by_y
LEFT JOIN inv_tw_indus_ocandf_by_e_im_by_y
ON inv_tw_indus_ocandf_by_e_num_by_y.核准年 = inv_tw_indus_ocandf_by_e_im_by_y.核准年
"""    
    
with engine.connect() as connection:
    result = connection.execute(text(query))
    data = result.fetchall()

# 將結果轉換成df
e_num_and_im = pd.DataFrame(data, columns=result.keys())

plt.rcParams["font.family"] = "Microsoft JhengHei"
plt.rcParams["font.size"] = 15
plt.rcParams["axes.unicode_minus"] = False

# 創建圖表和第一個Y軸
fig, ax1 = plt.subplots(figsize=(13, 8))

# 繪製件數（使用左Y軸）
ax1.set_xlabel("核准年")
ax1.set_ylabel("件數", color='tab:blue')
ax1.plot(e_num_and_im["核准年"], e_num_and_im["件數"], color='tab:blue', marker='o', label='投資金額')
ax1.tick_params(axis='y', labelcolor='tab:blue')

# 設置 x 軸間隔
ax1.xaxis.set_major_locator(MultipleLocator(2))

# 創建第二個Y軸，與第一個共享X軸
ax2 = ax1.twinx()
ax2.set_ylabel("金額-千美元", color='tab:red')
ax2.plot(e_num_and_im["核准年"], e_num_and_im["金額-千美元"], color='tab:red', marker='o', label='投資件數')
ax2.tick_params(axis='y', labelcolor='tab:red')

# 設置右側y軸格式
ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

# 添加網格線
ax1.grid(True)
ax2.grid(False)  # 如果只希望在ax1上添加網格線，可以將ax2.grid(False)

# 添加圖表標題
plt.title('投資件數與投資金額隨核准年的變化')

# 顯示圖表
fig.tight_layout()

plt.show()