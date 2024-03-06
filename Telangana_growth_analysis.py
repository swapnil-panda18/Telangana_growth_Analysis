
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import seaborn as sns
import  calendar

Transportation = pd.read_csv(r"C:\Users\Dell\Desktop\Projects\C7 Input Files_\dataset\fact_transport.csv")
Ipass=pd.read_csv(r"C:\Users\Dell\Desktop\Projects\C7 Input Files_\dataset\fact_TS_iPASS.csv")
Date=pd.read_csv(r"C:\Users\Dell\Desktop\Projects\C7 Input Files_\dataset\dim_date.csv")
stamp_registration=pd.read_csv(r"C:\Users\Dell\Desktop\Projects\C7 Input Files_\dataset\fact_stamps.csv")
district_names=pd.read_csv(r"C:\Users\Dell\Desktop\Projects\C7 Input Files_\dataset\dim_districts.csv")

# Stamp registration analysis:

# 1.How does the revenue generated from document registration vary
# across districts in Telangana? List down the top 5 districts that showed
# the highest revenue growth between FY 2019 and 2022.


# Calculate document registration revenue for FY 2019 and FY 2022 for every district


merged_df = pd.merge(stamp_registration,
                     Date, on='mnth', how='inner')
merged_df1 = pd.merge(merged_df,district_names,on='dist_code')

filtered_df = merged_df1[merged_df1['fiscal_year'].isin([2019,2022])]

revenue_2019 = filtered_df[filtered_df['fiscal_year'] == 2019].groupby('dist_code')['documents_registered_rev'].sum()
revenue_2022 = filtered_df[filtered_df['fiscal_year'] == 2022].groupby('dist_code')['documents_registered_rev'].sum()

total_revenue = pd.merge(revenue_2019,revenue_2022,on='dist_code')
total_district_revenue = pd.merge(total_revenue,district_names,on='dist_code')
total_district_revenue.columns=['District_code', 'Documents_registered_rev_2019', 'Documents_registered_rev_2022','District']

# Highest revenue growth b/w FY 2019 and FY 2022 for top 5 district
revenue_growth_df = ((total_district_revenue['Documents_registered_rev_2022']-total_district_revenue['Documents_registered_rev_2019'])/total_district_revenue['Documents_registered_rev_2019'])*100
total_district_revenue["rev_growth"] = revenue_growth_df
rev_growth_sort = total_district_revenue.sort_values(by='rev_growth',ascending=False)
top_5_districts = rev_growth_sort.head(5)
print(top_5_districts[['District','rev_growth']])


#1.1 Total Doc registration revenue across all districts

tot_doc_rev = merged_df1.groupby('district')['documents_registered_rev'].sum()
tot_revenue_sort = tot_doc_rev.sort_values(ascending=False)
print(tot_revenue_sort)



# 2.How does the revenue generated from document registration compare to the revenue generated from e-stamp challans across districts?
# List down the top 5 districts where e-stamps revenue contributes significantly more to the revenue than the documents in FY 2022?

print(merged_df1)

# Compare document registration to e-stamps challans
document_revenue = merged_df1.groupby('district')['documents_registered_rev'].sum()
document_revenue_sort = document_revenue.sort_values(ascending=False)
estamps_revenue = merged_df1.groupby('district')['estamps_challans_rev'].sum()
estamps_revenue_sort = estamps_revenue.sort_values(ascending=False)
doc_estamp_rev = pd.merge(document_revenue_sort,estamps_revenue_sort,on='district')
print(doc_estamp_rev)

# top 5 districts where e-stamps revenue more than document revenue in FY 2022

filtered_df1 = merged_df1[merged_df1['fiscal_year'].isin([2022])]
doc_rev_2022 = filtered_df1.groupby('district')['documents_registered_rev'].sum()
estamps_rev_2022 = filtered_df1.groupby('district')['estamps_challans_rev'].sum()
higher_estamps_revenue_districts = estamps_rev_2022[estamps_rev_2022 > doc_rev_2022]
higher_estamps_revenue_districts_sort = higher_estamps_revenue_districts.sort_values(ascending=False)
print(higher_estamps_revenue_districts_sort.head(5))


#3.Is there any alteration of e-Stamp challan count and document registration count pattern since the implementation of e-Stamp challan?
# If so, what suggestions would you propose to the government?

#plotting a time_series analysis
plt.figure(figsize=(12,6))
plt.plot(stamp_registration['mnth'],stamp_registration['estamps_challans_cnt'],label='E-stamp Challan Counts',marker='o',linestyle='-',color='blue')
plt.plot(stamp_registration['mnth'],stamp_registration['documents_registered_cnt'],label='Document Registration Counts',marker='x',linestyle='--',color='green')
plt.xlabel('Month')
plt.ylabel('Counts')
plt.title('E-stamp Challan Counts Vs Documents Registration Counts')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)

#plt.show()


# 4.Categorize districts into three segments based on their stamp
# registration revenue generation during the fiscal year 2021 to 2022.

revenue_2021_to_2022 = merged_df[(merged_df['fiscal_year']>=2021) & (merged_df['fiscal_year']<=2022)]
total_doc_revenue_by_district = revenue_2021_to_2022.groupby('dist_code')['documents_registered_rev'].sum().reset_index()
total_estamps_revenue_by_district = revenue_2021_to_2022.groupby('dist_code')['estamps_challans_rev'].sum().reset_index()
total_doc_revenue_by_district.rename(columns={'documents_registered_rev': 'total_doc_rev_2021_2022'},inplace=True)
total_estamps_revenue_by_district.rename(columns={'estamps_challans_rev': 'total_estamps_challans_rev_2021_2022'},inplace=True)
print(total_doc_revenue_by_district.head())
print(total_estamps_revenue_by_district.head())

percentiles_doc = total_doc_revenue_by_district['total_doc_rev_2021_2022'].quantile([0,0.33,0.67,1])
percentiles_estamps = total_estamps_revenue_by_district['total_estamps_challans_rev_2021_2022'].quantile([0,0.33,0.67,1])

total_doc_revenue_by_district['segment'] = pd.cut(total_doc_revenue_by_district['total_doc_rev_2021_2022'],
                                                  bins=percentiles_doc,
                                                  labels=['Low Revenue','Medium Revenue','High Revenue'],
                                                  include_lowest = True)
total_estamps_revenue_by_district['segment'] = pd.cut(total_estamps_revenue_by_district['total_estamps_challans_rev_2021_2022'],
                                                  bins=percentiles_doc,
                                                  labels=['Low Revenue','Medium Revenue','High Revenue'],
                                                  include_lowest = True)

print(total_doc_revenue_by_district)
print(total_estamps_revenue_by_district)

result_with_doc_district_names = pd.merge(total_doc_revenue_by_district,district_names,on='dist_code',how='left')
print(result_with_doc_district_names)
result_with_estamps_district_names = pd.merge(total_estamps_revenue_by_district,district_names,on='dist_code',how='left')
print(result_with_estamps_district_names)

custom_sort_order = ['High Revenue','Medium Revenue','Low Revenue']

result_with_doc_district_names['segment'] = pd.Categorical(result_with_doc_district_names['segment'],categories=custom_sort_order,ordered=True)
result_with_doc_district_names = result_with_doc_district_names.sort_values(by='segment')
result_with_doc_district_names.reset_index(drop=True,inplace=True)
print(result_with_doc_district_names)

result_with_estamps_district_names['segment'] = pd.Categorical(result_with_estamps_district_names['segment'],categories=custom_sort_order,ordered=True)
result_with_estamps_district_names = result_with_estamps_district_names.sort_values(by='segment')
result_with_estamps_district_names.reset_index(drop=True,inplace=True)
print(result_with_estamps_district_names)







##2. Transportation
#
# 1:Investigate whether there is any correlation between vehicle sales and specific months or seasons in different districts.
# Are there any months or seasons that consistently show higher or lower sales rate, and if yes, what could be the driving factors? (Consider Vehicle-Class category only)


print(Transportation.head())

vehicle_sales_data = Transportation[['dist_code', 'mnth', 'fuel_type_petrol', 'fuel_type_diesel', 'fuel_type_electric', 'fuel_type_others',
                                    'vehicleClass_MotorCycle', 'vehicleClass_MotorCar', 'vehicleClass_AutoRickshaw', 'vehicleClass_Agriculture', 'vehicleClass_others',
                                    'seatCapacity_1_to_3', 'seatCapacity_4_to_6', 'seatCapacity_above_6', 'Brand_new_vehicles', 'Pre-owned_vehicles',
                                    'category_Non-Transport', 'category_Transport']]




vehicle_class_type = ['vehicleClass_MotorCycle','vehicleClass_MotorCar','vehicleClass_AutoRickshaw','vehicleClass_Agriculture','vehicleClass_others']

vehicle_sales_data['total_sales'] = vehicle_sales_data[vehicle_class_type].sum(axis=1)
print( vehicle_sales_data)


monthly_total_sales = vehicle_sales_data.groupby('mnth')['total_sales'].sum()
print(monthly_total_sales)

#create a stem plot
plt.figure(figsize=(12, 6))
stemplot = plt.stem(monthly_total_sales.index,monthly_total_sales,label='Total Sales', linefmt ='--',markerfmt = 'o',orientation='vertical',)
plt.xlabel('Month')
plt.ylabel('Total Sales')
plt.title('Total Seasonal Trends in Vehicle Sales')
plt.legend()

plt.gcf().autofmt_xdate()
plt.xticks(rotation=45)
#plt.show()


# 2.How does the distribution of vehicles vary by vehicle class (MotorCycle, MotorCar, AutoRickshaw, Agriculture) across different districts?
# Are there any districts with a predominant preference for a specific vehicle class? Consider FY 2022 for analysis
#


merged_data = pd.merge(Transportation,Date,on='mnth')


merged_data = pd.merge(merged_data,district_names,on='dist_code')

merged_data_2022= merged_data[merged_data['fiscal_year'] == 2022]
print(merged_data_2022)

columns_of_interest = ['district', 'vehicleClass_MotorCycle', 'vehicleClass_MotorCar', 'vehicleClass_AutoRickshaw', 'vehicleClass_Agriculture', 'vehicleClass_others']

vehicle_distribution = merged_data_2022[columns_of_interest].groupby('district').sum()
print(vehicle_distribution)

# create a bar chart
ax = vehicle_distribution.plot(kind='bar',stacked=True,figsize=(12,6))
plt.xlabel("District name")
plt.ylabel("Total Vehicle Count")
plt.title("Distribution of Vehicles by Vehicle class(FY 2022")
plt.legend(title = 'Vehicle Class')

plt.gcf().autofmt_xdate()
#plt.show()


# 3.List down the top 3 and bottom 3 districts that have shown the highest and lowest vehicle sales growth during FY 2022 compared to FY 2021?
# (Consider and compare categories: Petrol, Diesel and Electric)

Merged_Data = pd.merge(Transportation,Date,on='mnth')
DATA_2021 = Merged_Data[Merged_Data['fiscal_year'] == 2021]
DATA_2022 = Merged_Data[Merged_Data['fiscal_year'] == 2022]

columns_of_interest_1 = ['dist_code', 'vehicleClass_MotorCycle', 'vehicleClass_MotorCar', 'vehicleClass_AutoRickshaw', 'vehicleClass_Agriculture', 'vehicleClass_others']

sales_2021 = DATA_2021[columns_of_interest_1].groupby('dist_code').sum()
sales_2022 = DATA_2022[columns_of_interest_1].groupby('dist_code').sum()
sales_2021 = pd.merge(sales_2021,district_names,on='dist_code')
sales_2022 = pd.merge(sales_2022,district_names,on='dist_code')

Total_sales_2022 = sales_2022['vehicleClass_MotorCycle']+sales_2022['vehicleClass_MotorCar']+sales_2022['vehicleClass_AutoRickshaw']+sales_2022['vehicleClass_Agriculture']+sales_2022['vehicleClass_others']
sales_2022['total sales 2022'] = Total_sales_2022
Total_sales_2021 = sales_2021['vehicleClass_MotorCycle']+sales_2021['vehicleClass_MotorCar']+sales_2021['vehicleClass_AutoRickshaw']+sales_2021['vehicleClass_Agriculture']+sales_2021['vehicleClass_others']
sales_2021['total sales 2021'] = Total_sales_2021

total_sales_merged = pd.merge(sales_2021,sales_2022,on='dist_code')

sales_growth = ((total_sales_merged['total sales 2022']-total_sales_merged['total sales 2021'])/ total_sales_merged['total sales 2021'])*100

total_sales_merged['Sales_growth_2021_2022'] = sales_growth
sales_growth_sorted =total_sales_merged.sort_values(by='Sales_growth_2021_2022',ascending=False)

top_3_districts= sales_growth_sorted.head(3)
bottom_3_districts=sales_growth_sorted.tail(3)

print("Top 3 districts with the highest sales growth:")
print(top_3_districts[['district_x', 'Sales_growth_2021_2022']])

print("Bottom 3 districts with the lowest sales growth:")
print(bottom_3_districts[['district_x', 'Sales_growth_2021_2022']])




## Ts-Ipass (Telangana State Industrial Project Approval and Self Certification System)
# 1.List down the top 5 sectors that have witnessed the most significant investments in FY 2022.
#


mer_df = pd.merge(Ipass,Date,on='mnth')
mer_df_2022 = mer_df[mer_df['fiscal_year'] == 2022]

sector_investment_2022 = mer_df_2022.groupby('sector')['investment_in_cr'].sum()

sector_investment_2022_sort = sector_investment_2022.sort_values(ascending=False)

sector_investment_2022_top_5 = sector_investment_2022_sort.head(5)
print("Top 5 sectors with the most Significant Investment in FY 2022:")
print(sector_investment_2022_top_5)


#Create a Bar chart
colors = ['red', 'blue', 'green', 'purple','yellow' ]
plt.figure(figsize=(8,8))
barplot = plt.bar(sector_investment_2022_top_5.index,sector_investment_2022_top_5,label= sector_investment_2022_top_5.index,alpha = 0.7,width= 0.3,color=colors)
plt.bar_label(barplot,labels = sector_investment_2022_top_5,label_type = 'edge',fontsize= 8,rotation=30)
plt.xlabel("Sector")
plt.ylabel("investment in cr")
plt.title("Top 5 Sectors with the most significant investment in FY 2022")
plt.xticks(fontsize = 6,rotation = 0)
plt.ylim([0,7000])
plt.legend()
plt.tight_layout()
#plt.show()


## 2.List down the top 3 districts that have attracted the most significant sector investments during FY 2019 to 2022?
# What factors could have led to the substantial investments in these particular districts?

mer_df1 = pd.merge(mer_df,district_names,on='dist_code')
mer_df1_2019_2022 = mer_df1.groupby('district')['investment_in_cr'].sum()

mer_df1_2019_2022_sort = mer_df1_2019_2022.sort_values(ascending=False)
mer_df1_2019_2022_sort_top_3 = mer_df1_2019_2022_sort.head(3)

print("Top 3 Districts with the Most Significant Sector Investments (FY 2019 to 2022):")
print(mer_df1_2019_2022_sort_top_3)


#Create a bar chart
colors =['Purple','Green','Red']
plt.figure(figsize=(12,8))
Barplot=plt.bar(mer_df1_2019_2022_sort_top_3.index,mer_df1_2019_2022_sort_top_3,label =mer_df1_2019_2022_sort_top_3.index,alpha = 0.7,width= 0.3, color =colors)
plt.bar_label(Barplot,label=mer_df1_2019_2022_sort_top_3,label_type= 'edge',fontsize = 10)
plt.xlabel("District")
plt.ylabel("Total Investment")
plt.title("Top 3 Districts with most significant investment ")
plt.legend()

plt.tight_layout()
#plt.show()



# 3.Is there any relationship between district investments, vehicles sales and stamps revenue within the same district between FY 2021 and 2022?

merge_ipass_district = pd.merge(Ipass,district_names,on='dist_code')
merge_ipass_district_invstmnt = merge_ipass_district.groupby('district')['investment_in_cr'].sum()
print(merge_ipass_district_invstmnt)

merge_transportation_district =pd.merge(Transportation,district_names,on='dist_code')
merge_transportation_district_invstmnt =merge_transportation_district.groupby('district')[['vehicleClass_MotorCycle', 'vehicleClass_MotorCar', 'vehicleClass_AutoRickshaw', 'vehicleClass_Agriculture', 'vehicleClass_others']].sum()
Total_vehicle_sales_total_invstmnt=merge_transportation_district_invstmnt['vehicleClass_MotorCycle']+merge_transportation_district_invstmnt['vehicleClass_MotorCar']+merge_transportation_district_invstmnt['vehicleClass_AutoRickshaw']+merge_transportation_district_invstmnt['vehicleClass_Agriculture']+merge_transportation_district_invstmnt['vehicleClass_others']
print(Total_vehicle_sales_total_invstmnt)


merge_stamps_district = pd.merge(stamp_registration,district_names,on='dist_code')
stamps_total_district_investment = merge_stamps_district.groupby('district')[['documents_registered_rev','estamps_challans_rev']].sum()
stamps_district_total_investment = stamps_total_district_investment['documents_registered_rev']+stamps_total_district_investment['estamps_challans_rev']
print(stamps_district_total_investment)



# 4 Are there any particular sectors that have shown substantial
#  growth in multiple districts in FY 2022?


ipass1 = pd.merge(Ipass,Date,on='mnth')
ipass3 = pd.merge(ipass1,district_names,on='dist_code')

ipass_2021 = ipass3[ipass3['fiscal_year'] == 2021]
ipass_2022 = ipass3[ipass3['fiscal_year'] == 2022]

investment_2021 = ipass_2021.groupby(['sector','district'])['investment_in_cr'].sum().reset_index()
investment_2022 = ipass_2022.groupby(['sector','district'])['investment_in_cr'].sum().reset_index()


total_investment_2021 = investment_2021.groupby('sector')['investment_in_cr'].sum().reset_index()
total_investment_2022 = investment_2022.groupby('sector')['investment_in_cr'].sum().reset_index()


investment_comparison = pd.merge(total_investment_2021,total_investment_2022,on='sector',suffixes=('_2021','_2022'))


# threshold for substantial investment growth
threshold = 100

substantial_investment_growth = investment_comparison[investment_comparison['investment_in_cr_2022'] > threshold]

## Count the number of districts with investments for each sector
district_count = investment_2022.groupby('sector')['district'].count().reset_index()

substantial_investment_growth = pd.merge(substantial_investment_growth,district_count,on='sector',how='left')

substantial_investment_growth.rename(columns={'district': 'no of districts'}, inplace=True)

substantial_investment_growth = substantial_investment_growth.sort_values(by='no of districts',ascending =False)

print("Sectors with Substantial Investment in multiple districts between FY 2021 and FY 2022 (sorted by District Count):")
print(substantial_investment_growth[['sector','investment_in_cr_2022','no of districts']])


#create a bar chart

plt.figure(figsize=(12,6))
Barplot=plt.bar(substantial_investment_growth['sector'],substantial_investment_growth['no of districts'],color='skyblue')
plt.bar_label(Barplot,label=substantial_investment_growth['no of districts'],label_type ='edge',fontsize=8)
plt.xlabel('Sector')
plt.ylabel('Number of districts')
plt.title('Sector with Substantial Investment in Multiple Districts (Sorted by District Count)')
plt.gcf().autofmt_xdate()
plt.xticks(fontsize= 7,rotation=45)
plt.tight_layout()
#plt.show()

# 5.Can we identify any seasonal patterns or cyclicality in the investment trends for specific sectors?
# Do certain sectors experience higher investments during particular months?
#
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 3)
pd.set_option('display.max_rows', 74)
merge_1 = pd.merge(Ipass,Date,on="mnth")
seasonal_investment = merge_1.groupby(['fiscal_year','sector'])['investment_in_cr'].sum().reset_index()

print(seasonal_investment)


### # Secondary research

# ### The top 5 districts to buy commercial properties in Telangana.


merge_2 = pd.merge(Ipass,district_names,on='dist_code')
investments_total = merge_2.groupby('district')['investment_in_cr'].sum().reset_index()
investments_total = investments_total.sort_values(by='investment_in_cr',ascending=False)
investments_total = investments_total.head(5)
print(investments_total)

#plot a line graph
plt.figure(figsize=(12,6))
plt.plot(investments_total['district'],investments_total['investment_in_cr'],marker='o',linestyle='-',color='blue')
plt.xlabel('District')
plt.ylabel('investment_in_cr')
plt.title('Top 5 district to buy commercial properties')
plt.tight_layout()
for i,v in enumerate(investments_total['investment_in_cr']):
    plt.text(i,v,str(v))
plt.show()




