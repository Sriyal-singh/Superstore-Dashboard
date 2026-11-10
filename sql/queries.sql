-- Superstore SQL analysis (SQLite). Run `python analysis.py` first to create superstore.db, then:
--   sqlite3 superstore.db < sql/queries.sql      (or open in DB Browser for SQLite / any SQL client)

-- 1. KPIs
SELECT ROUND(SUM(Sales),0) AS revenue, ROUND(SUM(Profit),0) AS profit,
       COUNT(DISTINCT Order_ID) AS orders, ROUND(SUM(Sales)/COUNT(DISTINCT Order_ID),2) AS avg_order_value
FROM orders;

-- 2. Monthly revenue and profit
SELECT Month, ROUND(SUM(Sales),0) AS revenue, ROUND(SUM(Profit),0) AS profit
FROM orders GROUP BY Month ORDER BY Month;

-- 3. Month-over-month revenue growth (window function)
WITH monthly AS (SELECT Month, SUM(Sales) AS revenue FROM orders GROUP BY Month)
SELECT Month, ROUND(revenue,0) AS revenue,
       ROUND(100.0*(revenue - LAG(revenue) OVER (ORDER BY Month)) / LAG(revenue) OVER (ORDER BY Month),1) AS mom_growth_pct
FROM monthly ORDER BY Month;

-- 4. Top 10 customers by revenue
SELECT Customer_Name, ROUND(SUM(Sales),0) AS revenue, ROUND(SUM(Profit),0) AS profit
FROM orders GROUP BY Customer_Name ORDER BY revenue DESC LIMIT 10;

-- 5. Top 10 products by profit
SELECT Product_Name, ROUND(SUM(Profit),0) AS profit, SUM(Quantity) AS units
FROM orders GROUP BY Product_Name ORDER BY profit DESC LIMIT 10;

-- 6. Regional performance with margin
SELECT Region, ROUND(SUM(Sales),0) AS revenue, ROUND(SUM(Profit),0) AS profit,
       ROUND(100.0*SUM(Profit)/SUM(Sales),1) AS margin_pct
FROM orders GROUP BY Region ORDER BY profit DESC;

-- 7. Loss-making sub-categories
SELECT Category, Sub_Category, ROUND(SUM(Profit),0) AS profit
FROM orders GROUP BY Category, Sub_Category HAVING SUM(Profit) < 0 ORDER BY profit;

-- 8. Does discounting hurt profit?
SELECT CASE WHEN Discount = 0 THEN 'None' WHEN Discount <= .2 THEN 'Low (<=20%)' ELSE 'High (>20%)' END AS discount_band,
       COUNT(*) AS lines, ROUND(AVG(Profit),2) AS avg_profit
FROM orders GROUP BY discount_band;

-- 9. Rank products within each category (RANK window)
SELECT * FROM (
  SELECT Category, Product_Name, ROUND(SUM(Sales),0) AS revenue,
         RANK() OVER (PARTITION BY Category ORDER BY SUM(Sales) DESC) AS rnk
  FROM orders GROUP BY Category, Product_Name) WHERE rnk <= 3;

-- 10. Customers who ordered in 3+ different years (loyal customers)
SELECT Customer_Name, COUNT(DISTINCT Year) AS years_active, ROUND(SUM(Sales),0) AS revenue
FROM orders GROUP BY Customer_Name HAVING COUNT(DISTINCT Year) >= 4 ORDER BY revenue DESC LIMIT 10;
