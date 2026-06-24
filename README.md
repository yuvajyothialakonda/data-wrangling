# data-wrangling
Data Cleaning and Preprocessing – Description
This task focuses on preparing a raw sales dataset for analysis by identifying data quality issues and applying systematic cleaning techniques. The goal is to transform unstructured and inconsistent data into a clean, reliable, and analysis-ready dataset.

1. Data Loading
The dataset is loaded from an Excel file.
The structure (rows and columns) is inspected to understand the data.

2. Data Quality Assessment
Before cleaning, the dataset is analyzed to find issues such as:
Missing values (e.g., Age, City)
Duplicate records (same rows or repeated Order_IDs)
Inconsistent text formatting (extra spaces, mixed case)
Outliers in numerical columns (Age, Quantity, Sales)

3. Data Cleaning
The following fixes are applied:
Duplicate Order_IDs Fixed
Missing Values Handled
Text Formatting Standardized
Date Column Converted
Duplicate Rows Removed

4. Feature Engineering
New useful columns are created:
Age_Group → Categorizes customers (18–25, 26–35, etc.)
Order_Year, Month, Weekday → Time-based analysis
Sale_Size → Classifies sales (Small, Medium, Large)

5. Output Generation
Cleaned dataset is saved as a new Excel file
Data Quality Report is generated summarizing all issues found

