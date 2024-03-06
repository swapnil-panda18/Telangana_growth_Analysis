create database Telangana_growth;
use Telangana_growth;
select * from dim_date;
select * from dim_districts;
select * from fact_stamps;
select * from fact_transport;
select * from fact_ts_ipass;

-- Stamps Registration
-- document registration vary across districts in Telangana
with cte as
(select district,sum(documents_registered_rev) as total_doc_rev
from fact_stamps as a 
join dim_districts as b
on a.dist_code=b.dist_code
group by district
order by total_doc_rev DESC)

select district,
case
when total_doc_rev >= 1000000000
then CONCAT(ROUND(total_doc_rev / 1000000000,2),'B')
when total_doc_rev >= 1000000 then  CONCAT(ROUND(total_doc_rev / 1000000,2),'B')
Else total_doc_rev
end as total_revenue
from cte;

-- List down the top 5 districts that showed the highest revenue growth between FY 2019 and 2022.

with cte as 
(select district,
sum(case
when fiscal_year = 2022
then documents_registered_rev
else 0
end) as tot_doc_rev_2022,
sum(case
when fiscal_year = 2019
then documents_registered_rev
else 0
end) as tot_doc_rev_2019
from fact_stamps as a 
join dim_districts as b
on a.dist_code=b.dist_code
join dim_date as c
on a.month=c.month
group by district
order by tot_doc_rev_2022 DESC,tot_doc_rev_2019 DESC)

select district,tot_doc_rev_2022,tot_doc_rev_2019,
(tot_doc_rev_2022-tot_doc_rev_2019) as revenue_growth,
round((tot_doc_rev_2022-tot_doc_rev_2019)/(tot_doc_rev_2019)*100,2) as revenue_growth_percentage
from cte 
order by revenue_growth_percentage DESC;


-- revenue generated from document registration compareto the revenue generated from e-stamp challans across districts

select district,sum(documents_registered_rev) as tot_doc_rev,
sum(estamps_challans_rev) as tot_estamps_rev
from fact_stamps as a
join dim_districts as b
on a.dist_code=b.dist_code
group by district
order by tot_doc_rev DESC,tot_estamps_rev DESC;

-- top 5 districts where e-stamps revenue contributes significantly more to the revenue than the documents in FY 2022

select district,
sum(case
when estamps_challans_rev > documents_registered_rev
then estamps_challans_rev
else 0
end) as result_echallan
from fact_stamps as a 
join dim_districts as b
on a.dist_code=b.dist_code
join dim_date as c
on a.month=c.month
where fiscal_year = 2022
group by district
order by result_echallan DESC
limit 5;

-- e-Stamp challan count and document registration count pattern

select year(month),sum(documents_registered_cnt) as tot_doc_cnt,
sum(estamps_challans_cnt) as tot_challans_cnt,
(sum(estamps_challans_cnt)-sum(documents_registered_cnt)) as change_in_cnt
from fact_stamps
group by year(month)
order by year(month);


-- Categorize districts into three segments  during the fiscal year 2021 to 2022.

select district,
sum(documents_registered_rev) as tot_doc_rev_2022,
case
when sum(documents_registered_rev) >= 10000000000
then "High Revenue"
when sum(documents_registered_rev) >= 600000000
then "Medium Revenue"
else "Low Revenue"
end as revenue_category
from fact_stamps as a 
join dim_districts as b
on a.dist_code=b.dist_code
join dim_date as c
on a.month=c.month
where fiscal_year between 2021 and 2022
group by district
order by tot_doc_rev_2022 Desc;

-- Transportation
-- Investigate whether there is any correlation between vehicle sales and specific months or seasons in different districts

select month, sum(vehicleClass_MotorCycle)+sum(vehicleClass_MotorCar)+sum(vehicleClass_AutoRickshaw)+
sum(vehicleClass_Agriculture)+sum(vehicleClass_others) as tot_Vehicle_sales
from fact_transport
group by month
order by tot_Vehicle_sales DESC;


--  distribution of vehicles vary by vehicle class (MotorCycle, MotorCar, AutoRickshaw, Agriculture) across different districts

select a.district as district_name,
SUM(b.vehicleClass_MotorCycle) as total_MotorCycle,
SUM(b.vehicleClass_MotorCar) as total_MotorCar,
SUM(b.vehicleClass_AutoRickshaw) as total_AutoRickshaw,
SUM(b.vehicleClass_Agriculture) as total_Agriculture,
SUM(b.vehicleClass_others) as total_otherclass
from fact_transport as b
join dim_districts as a
on b.dist_code=a.dist_code
group by district_name
order by total_MotorCycle DESC;


-- List down the top 3 and bottom 3 districts that have shown the highest and lowest vehicle sales growth during FY 2022 compared to FY 2021? (Consider and compare categories: Petrol, Diesel and Electric)
-- for diesel

select district,
total_sales_2022-total_sales_2021 as sales_growth,
round((total_sales_2022-total_sales_2021)/(total_sales_2021)*100,2) as sales_growth_percentage
from
(select district,
sum(case
when year(month) = 2022
then fuel_type_diesel
else 0
end) as  total_sales_2022,
sum(case
when year(month) = 2021
then fuel_type_diesel
else 0
end) as total_sales_2021
from fact_transport as a 
join dim_districts as b
on a.dist_code=b.dist_code
group by district) as sales_by_district
order by sales_growth_percentage DESC;


-- for electric

select district,
total_sales_2022-total_sales_2021 as sales_growth,
round((total_sales_2022-total_sales_2021)/(total_sales_2021)*100,2) as sales_growth_percentage
from
(select district,
sum(case
when year(month) = 2022
then fuel_type_electric
else 0
end) as  total_sales_2022,
sum(case
when year(month) = 2021
then fuel_type_electric
else 0
end) as total_sales_2021
from fact_transport as a 
join dim_districts as b
on a.dist_code=b.dist_code
group by district) as sales_by_district
order by sales_growth_percentage DESC;


-- for petrol

select district,
total_sales_2022-total_sales_2021 as sales_growth,
round((total_sales_2022-total_sales_2021)/(total_sales_2021)*100,2) as sales_growth_percentage
from
(select district,
sum(case
when year(month) = 2022
then fuel_type_petrol
else 0
end) as  total_sales_2022,
sum(case
when year(month) = 2021
then fuel_type_petrol
else 0
end) as total_sales_2021
from fact_transport as a 
join dim_districts as b
on a.dist_code=b.dist_code
group by district) as sales_by_district
order by sales_growth_percentage DESC;

-- Ipass
-- top 5 sectors that have witnessed the most significant investments in FY 2022.

with cte as 
(select a.month,a.sector,a.investment_in_cr,b.fiscal_year
from fact_ts_ipass as a
join dim_date as b
on a.month=b.month
where b.fiscal_year = 2022)

select sector,sum(investment_in_cr) as total_investment
from cte
group by sector
order by total_investment DESC
limit 5;

-- top 3 districts that have attracted the most significant sector investments during FY 2019 to 2022

with cte as 
(select a.dist_code,a.investment_in_cr,b.district
from fact_ts_ipass as a
join dim_districts as b
on a.dist_code=b.dist_code)

select district,sum(investment_in_cr) as total_investment
from cte 
group by district
order by total_investment DESC
limit 3;


-- relationship between sector investments, vehicles  sales and stamps revenue in the same district between FY 2021 and 2022

with investment_cte as
(select district,sum(investment_in_cr) as total_investment
from fact_ts_ipass as a
join dim_districts as b
on a.dist_code=b.dist_code
where year(month) between 2021 and 2022
group by district)

,vehicle_sales_cte as 
(select district,sum(vehicleClass_MotorCycle)+sum(vehicleClass_MotorCar)+sum(vehicleClass_AutoRickshaw)+
sum(vehicleClass_Agriculture)+sum(vehicleClass_others) as tot_Vehicle_sales
from fact_transport as a
join dim_districts as b
on a.dist_code=b.dist_code
where year(month) between 2021 and 2022
group by district)

,stamps_rev_cte as
(select district,
sum(documents_registered_rev)+sum(estamps_challans_rev) as total_stamps_revenue
from fact_stamps as a
join dim_districts as b
on a.dist_code=b.dist_code
where year(month) between 2021 and 2022
group by district)

select I.district,I.total_investment,V.tot_vehicle_sales,S.total_stamps_revenue
from investment_cte as I
join vehicle_sales_cte as V
on I.district=V.district
join stamps_rev_cte as S
on I.district=S.district;

-- particular sectors that have shown substantial growth in multiple districts in FY 2022?

select sector, count(distinct district) as district_count, sum(investment_in_cr) as total_investment
from fact_ts_ipass as a 
join dim_districts as b
on a.dist_code=b.dist_code
where year(month) between 2021 and 2022
group by sector 
order by district_count DESC;

