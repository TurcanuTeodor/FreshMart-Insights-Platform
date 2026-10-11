/*==========================================================================
  SOFTWARE PACKAGES PROJECT – SAS PROGRAMMING PART
  Organization: FreshMart | Dataset: FreshMart_Dataset.csv
  9,994 orders | 2014–2017
==========================================================================*/

ods graphics on;
options nodate nonumber ls=180 ps=60;

/*==========================================================================
  1. create sas dataset
==========================================================================*/

proc import datafile="/home/u64519670/FreshMart_Dataset.csv"
            out=work.orders_raw
            dbms=csv
            replace;
    getnames=yes;
run;

data work.orders;
    set work.orders_raw;
    if Sales > 0 then Profit_Margin = (Profit / Sales) * 100;
    else Profit_Margin = 0;
    Ship_Days = Ship_Duration_Days;
    format Order_Date Ship_Date date9.
           Sales Profit dollar10.2
           Profit_Margin 6.1;
    label Ship_Days     = "Days to Ship"
          Profit_Margin = "Profit Margin (%)";
run;

proc contents data=work.orders varnum; run;
proc print data=work.orders (obs=5) noobs; run;


/*==========================================================================
  2. user defined formats
==========================================================================*/

proc format;
    value $seg_fmt
        'Consumer'    = 'B2C - Consumer'
        'Corporate'   = 'B2B - Corporate'
        'Home Office' = 'Home Office'
        other         = 'Unknown';

    value $reg_fmt
        'East'    = 'East Region'
        'West'    = 'West Region'
        'Central' = 'Central Region'
        'South'   = 'South Region'
        other     = 'Other';

    value disc_tier
        0         = 'No Discount'
        0.01-0.20 = 'Low (1-20%)'
        0.21-0.40 = 'Medium (21-40%)'
        0.41-high = 'High (>40%)';

    value profit_band
        low  -< 0  = 'Loss'
        0    -< 50 = 'Low Profit'
        50   -<200 = 'Medium Profit'
        200  - high= 'High Profit';
run;

/*apply formats */
data work.orders;
    set work.orders;
    format Segment  $seg_fmt.
           Region   $reg_fmt.
           Discount disc_tier.
           Profit   profit_band.;
run;

proc freq data=work.orders;
    tables Segment Region Discount / nocum;
    title "Frequency Tables with User-Defined Formats";
run;
title;


/*==========================================================================
  3. iterative and conditional process
==========================================================================*/

data work.orders_classified;
    set work.orders;
 
    length Perf_Class $20;
    if      Profit > 200 then Perf_Class = 'Excellent';
    else if Profit > 50  then Perf_Class = 'Good';
    else if Profit >= 0  then Perf_Class = 'Marginal';
    else                      Perf_Class = 'Loss-Making';

    length Discount_Flag $3;
    if Discount >= 0.4 then Discount_Flag = 'Yes';
    else                    Discount_Flag = 'No';

    length Ship_Speed $10;
    select;
        when (Ship_Days <= 1) Ship_Speed = 'Express';
        when (Ship_Days <= 3) Ship_Speed = 'Fast';
        when (Ship_Days <= 5) Ship_Speed = 'Standard';
        otherwise              Ship_Speed = 'Slow';
    end;
run;

proc freq data=work.orders_classified;
    tables Perf_Class Discount_Flag Ship_Speed / nocum;
    title "Order Classification Results";
run;
title;


/*==========================================================================
  4. create data subsets
==========================================================================*/

/* subset 1: technology orders only */
data work.tech_orders;
    set work.orders_classified;
    where Category = 'Technology';
run;

/* subset 2: loss-making orders */
data work.loss_orders;
    set work.orders_classified;
    where Profit < 0;
run;

/* subset 3: year 2017 only */
data work.orders_2017;
    set work.orders_classified;
    where Order_Year = 2017;
run;

proc print data=work.loss_orders (obs=10) noobs;
    var Order_ID Customer_Name Category Sub_Category Sales Profit Discount;
    title "Sample of Loss-Making Orders";
run;
title;


/*==========================================================================
  5. using sas func
==========================================================================*/

data work.orders_enriched;
    set work.orders_classified;

    /* date functions */
    Qtr_Label  = cats('Q', Order_Quarter, '-', Order_Year);
    Month_Name = put(Order_Date, monname3.);
    /*string functions */
    Customer_Last = scan(Customer_Name, -1, ' ');
    State_Upper   = upcase(State);
    Product_Short = substr(Product_Name, 1, 40);
    /*numeric functions */
    Log_Sales     = log(Sales);
    Sales_Rounded = round(Sales, 10);
    Abs_Profit    = abs(Profit);
    Profit_Sign   = ifc(Profit >= 0, 'Positive', 'Negative');

    format Qtr_Label $7. Log_Sales 8.3 Sales_Rounded dollar10.;
run;

proc print data=work.orders_enriched (obs=5) noobs;
    var Order_ID Customer_Name Customer_Last Qtr_Label Month_Name
        Sales Log_Sales Sales_Rounded Profit Profit_Sign Ship_Days;
    title "Dataset Enriched with SAS Function Columns";
run;
title;


/*==========================================================================
  6. data merge and proc sql
==========================================================================*/

/*reference table: regional budgets */
data work.region_budget;
    length Region $10;
    input Region $ Budget;
    datalines;
East    1500000
West    1800000
Central 1200000
South    900000
;
run;

/* actual sales by region via PROC SQL */
proc sql;
    create table work.region_actuals as
        select  Region,
                sum(Sales)  as Actual_Sales  format=dollar14.2,
                sum(Profit) as Actual_Profit format=dollar14.2,
                count(*)    as Num_Orders
        from    work.orders
        group by Region;
quit;

/* data step merge: budget vs actual */
proc sort data=work.region_actuals; by Region; run;
proc sort data=work.region_budget;  by Region; run;

data work.region_vs_budget;
    merge work.region_actuals (in=a)
          work.region_budget  (in=b);
    by Region;
    if a and b;
    Budget_Variance = Actual_Sales - Budget;
    Pct_vs_Budget   = (Actual_Sales / Budget) * 100;
    format Budget dollar14.2
           Budget_Variance dollar14.2
           Pct_vs_Budget 6.1;
run;

proc print data=work.region_vs_budget noobs;
    title "Budget vs. Actual Sales by Region (DATA STEP MERGE)";
run;
title;

/* proc sql join: attach avg category margin to each order */
proc sql;
    create table work.orders_with_cat_avg as
        select  a.*,
                b.Avg_Category_Margin,
                (a.Profit_Margin - b.Avg_Category_Margin)
                    as Margin_Deviation format=6.2
                    label="Deviation from Category Avg (%)"
        from    work.orders_enriched as a
        left join
               (select  Category,
                        mean(Profit_Margin) as Avg_Category_Margin format=6.2
                from    work.orders_enriched
                group by Category) as b
        on a.Category = b.Category;
quit;


/*==========================================================================
  7. arrays, quarterly sales analysis
==========================================================================*/

proc sql;
    create table work.cat_quarterly_wide as
        select  Category,
                sum(case when Order_Quarter=1 then Sales else 0 end) as Q1_Sales,
                sum(case when Order_Quarter=2 then Sales else 0 end) as Q2_Sales,
                sum(case when Order_Quarter=3 then Sales else 0 end) as Q3_Sales,
                sum(case when Order_Quarter=4 then Sales else 0 end) as Q4_Sales
        from    work.orders
        group by Category;
quit;

data work.cat_quarterly_analysis;
    set work.cat_quarterly_wide;

    array q_sales {4} Q1_Sales Q2_Sales Q3_Sales Q4_Sales;
    array q_share {4} Q1_Share Q2_Share Q3_Share Q4_Share;

    /* total annual sales */
    Annual_Sales = 0;
    do i = 1 to 4;
        Annual_Sales + q_sales{i};
    end;

    /* quarterly share percentages */
    do i = 1 to 4;
        if Annual_Sales > 0
            then q_share{i} = (q_sales{i} / Annual_Sales) * 100;
        else     q_share{i} = 0;
    end;

    /*find peak quarter iteratively */
    Peak_Sales = 0;
    Peak_Qtr   = 0;
    do i = 1 to 4;
        if q_sales{i} > Peak_Sales then do;
            Peak_Sales = q_sales{i};
            Peak_Qtr   = i;
        end;
    end;
    Peak_Quarter = cats('Q', Peak_Qtr);
    drop i;

    format Annual_Sales Peak_Sales Q1_Sales-Q4_Sales dollar14.2
           Q1_Share-Q4_Share 5.1;
run;

proc print data=work.cat_quarterly_analysis noobs;
    var Category Annual_Sales
        Q1_Sales Q1_Share Q2_Sales Q2_Share
        Q3_Sales Q3_Share Q4_Sales Q4_Share
        Peak_Quarter;
    title "Quarterly Sales Analysis by Category (Array-Based)";
run;
title;


/*==========================================================================
  8. report procedures
==========================================================================*/

/*proc report: sales & profit by region and category */
proc report data=work.orders_classified nowd headline headskip;
    column Region Category Sales Profit Profit_Margin Quantity;

    define Region        / group  "Region"         width=15;
    define Category      / group  "Category"       width=18;
    define Sales         / sum    "Total Sales"    format=dollar14.2;
    define Profit        / sum    "Total Profit"   format=dollar14.2;
    define Profit_Margin / mean   "Avg Margin (%)" format=6.2;
    define Quantity      / sum    "Units Sold"     format=comma10.;

    break after Region / summarize suppress skip;
    rbreak after / summarize;

    title  "Sales and Profit by Region and Category";
    title2 "FreshMart – 2014 to 2017";
run;
title; title2;

/* proc tabulate: segmentxcategoryxyear */
proc tabulate data=work.orders_classified format=dollar12.2;
    class  Segment Category Order_Year;
    var    Sales Profit;
    table  Segment * Category,
           Order_Year * (Sales * Sum  Profit * Sum)
           / box="FreshMart KPIs";
    title "Sales and Profit by Segment, Category, and Year";
run;
title;

/* proc print: top 10 most profitable orders */
proc sort data=work.orders_classified out=work.top10;
    by descending Profit;
run;
proc print data=work.top10 (obs=10) noobs label;
    var Order_ID Order_Date Customer_Name Segment Category
        Sales Profit Perf_Class;
    title "Top 10 Most Profitable Orders";
run;
title;


/*==========================================================================
  [9] STATISTICAL PROCEDURES
==========================================================================*/

/* proc means: descriptive statistics by category */
proc means data=work.orders_classified n mean std min max sum maxdec=2;
    class Category;
    var   Sales Profit Quantity Discount Ship_Days;
    title "Descriptive Statistics by Category";
run;
title;

/* prog freq: ship mode vs segment with chisquare */
proc freq data=work.orders_classified;
    tables Ship_Mode * Segment / chisq nocum;
    title "Ship Mode by Customer Segment";
run;
title;

/* proc corr: correlation matrix */
proc corr data=work.orders_classified pearson;
    var Sales Profit Discount Quantity Ship_Days;
    title "Pearson Correlation Matrix";
run;
title;

/* proc req: profit ~ sales + discount + quantity */
proc reg data=work.orders_classified plots=diagnostics;
    model Profit = Sales Discount Quantity / vif clb;
    title "Multiple Regression: Profit ~ Sales + Discount + Quantity";
run;
quit;
title;


/*==========================================================================
 10. graphs
==========================================================================*/

/* data for charts */
proc sql;
    create table work.chart_region as
        select  Region, Category,
                sum(Sales)          as Total_Sales  format=dollar14.2,
                sum(Profit)         as Total_Profit format=dollar14.2,
                mean(Profit_Margin) as Avg_Margin   format=6.1
        from    work.orders_enriched
        group by Region, Category;

    create table work.chart_monthly as
        select  Order_Year,
                Order_Month,
                mdy(Order_Month, 1, Order_Year) as Date_Label format=monyy7.,
                sum(Sales)  as Monthly_Sales  format=dollar14.2,
                sum(Profit) as Monthly_Profit format=dollar14.2
        from    work.orders
        group by Order_Year, Order_Month;
quit;

/* graph 1: grouped bar, sales by region and category */
proc sgplot data=work.chart_region;
    vbar Region / response=Total_Sales group=Category
         groupdisplay=cluster fillattrs=(transparency=0.15);
    xaxis label="Region";
    yaxis label="Total Sales (USD)" grid;
    keylegend / title="Product Category";
    title "Total Sales by Region and Product Category";
run;
title;

/* graph 2: scatter, sales vs profit by category */
proc sgplot data=work.orders_enriched (obs=3000);
    scatter x=Sales y=Profit / group=Category
            markerattrs=(size=5 symbol=circlefilled)
            transparency=0.5;
    refline 0 / axis=y lineattrs=(color=red thickness=2 pattern=dash)
                label="Break-even";
    xaxis label="Sales (USD)";
    yaxis label="Profit (USD)" grid;
    keylegend / title="Category";
    title "Sales vs. Profit by Product Category";
run;
title;

/* graph 3: histogram, profit distribution with density curve */
proc sgplot data=work.orders_classified;
    histogram Profit / binwidth=50
              fillattrs=(color=steelblue transparency=0.3);
    density Profit / type=kernel
              lineattrs=(color=darkred thickness=2);
    refline 0 / axis=x lineattrs=(color=red pattern=dash) label="Zero";
    xaxis label="Profit (USD)" min=-500 max=1000;
    yaxis label="Number of Orders";
    title "Distribution of Order Profit";
run;
title;

/* graph 4: line chart, monthly sales trend */
proc sgplot data=work.chart_monthly;
    series x=Date_Label y=Monthly_Sales /
           lineattrs=(color=steelblue thickness=2)
           markers markerattrs=(symbol=circlefilled size=6);
    xaxis label="Month" grid;
    yaxis label="Total Sales (USD)" grid;
    title "Monthly Sales Trend – 2014 to 2017";
run;
title;

/* graph 5: box plot, profit by category */
proc sgplot data=work.orders_classified;
    vbox Profit / category=Category
                  fillattrs=(transparency=0.3)
                  outlierattrs=(size=3);
    refline 0 / axis=y lineattrs=(color=red pattern=dash);
    yaxis label="Profit (USD)" min=-500 max=3000 grid;
    xaxis label="Product Category";
    title "Profit Distribution by Product Category";
run;
title;

/* graph 6: panel, discount vs profit by category */
proc sgpanel data=work.orders_enriched;
    panelby Category / columns=3 novarname;
    scatter x=Discount y=Profit /
            markerattrs=(size=4 symbol=circlefilled)
            transparency=0.6;
    rowaxis label="Profit (USD)";
    colaxis label="Discount Rate";
    title "Discount Rate vs. Profit by Product Category";
run;
title;

