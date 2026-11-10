# Power BI dashboard guide (Superstore)

**Data:** Get Data -> Text/CSV -> `superstore_for_powerbi.csv`. Mark `Order Date` as a Date type, then
*Modeling -> New table* to create a calendar: `Calendar = CALENDAR(MIN(Orders[Order Date]), MAX(Orders[Order Date]))`,
relate `Calendar[Date]` -> `Orders[Order Date]`.

**Measures**
```DAX
Revenue = SUM ( Orders[Sales] )
Profit = SUM ( Orders[Profit] )
Orders = DISTINCTCOUNT ( Orders[Order ID] )
Avg Order Value = DIVIDE ( [Revenue], [Orders] )
Profit Margin % = DIVIDE ( [Profit], [Revenue] )
Revenue LY = CALCULATE ( [Revenue], SAMEPERIODLASTYEAR ( 'Calendar'[Date] ) )
YoY Growth % = DIVIDE ( [Revenue] - [Revenue LY], [Revenue LY] )
```
**Layout:** 4 KPI cards (Revenue, Profit, Orders, AOV) -> line chart (Month x Revenue, Profit) -> bar chart (Top 10 customers, Top N filter)
-> bar chart (Top 10 products) -> **filled map** (State, colour saturation = Profit) -> donut (Category share).
**Slicers:** Year, Region, Segment, Category. Turn on *Sync slicers* and cross-filtering. Add a tooltip page with margin %.
Screenshot the finished page into `images/dashboard.png` and reference it in the README.

**Excel version:** Insert -> PivotTable on the CSV, then Insert -> Slicer (Region, Segment) + PivotChart (Month x Sales).
