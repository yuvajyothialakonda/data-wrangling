
import pandas as pd

RAW_FILE = "../data/ApexPlanet_DataAnalytics_Dataset.xlsx"
CLEAN_FILE = "../output/Cleaned_Sales_Dataset.xlsx"
REPORT_FILE = "../output/Data_Quality_Report.txt"


def load_data(path):
    print("Loading the raw dataset...")
    df = pd.read_excel(path, sheet_name="Sales_Dataset")
    print(f"Loaded {len(df)} rows and {len(df.columns)} columns.\n")
    return df


def assess_quality(df):
    """Just looks at the data and writes down what's wrong with it.
    Nothing is changed here - this is purely the 'inspection' step."""
    report_lines = []
    report_lines.append("DATA QUALITY ASSESSMENT")
    report_lines.append("=" * 50)

    # 1. Missing values
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    report_lines.append("\n1. Missing values found:")
    if missing.empty:
        report_lines.append("   None")
    else:
        for col, count in missing.items():
            report_lines.append(f"   - {col}: {count} missing")

    # 2. Duplicate Order_IDs (same ID reused for different real orders)
    dupe_ids = df["Order_ID"].duplicated().sum()
    report_lines.append(f"\n2. Duplicate Order_IDs: {dupe_ids}")
    report_lines.append("   (Same Order_ID appears on different transactions - a data entry glitch)")

    # 3. Fully duplicated rows (exact copies)
    full_dupes = df.duplicated().sum()
    report_lines.append(f"\n3. Fully duplicated rows: {full_dupes}")

    # 4. Inconsistent text formatting (extra spaces, mixed case) in key text columns
    text_cols = ["City", "Product", "Category", "Gender"]
    report_lines.append("\n4. Text formatting check (City/Product/Category/Gender):")
    for col in text_cols:
        has_spaces = df[col].dropna().apply(lambda x: x != x.strip()).sum()
        report_lines.append(f"   - {col}: {has_spaces} values with extra leading/trailing spaces")

    # 5. Outlier check on numeric columns using the IQR method
    report_lines.append("\n5. Outlier check (IQR method) on numeric columns:")
    for col in ["Age", "Quantity", "Unit_Price", "Total_Sales"]:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = df[(df[col] < low) | (df[col] > high)]
        report_lines.append(f"   - {col}: {len(outliers)} outliers (expected range {low:.0f} to {high:.0f})")

    print("\n".join(report_lines))
    return report_lines


def clean_data(df):
    """This is where we actually fix the issues found above."""
    df = df.copy()

    # --- Fix 1: Order_ID duplicates ---
    # A handful of Order_IDs were reused across different, unrelated transactions.
    # Since Order_ID should be a unique key, we re-number the duplicates so every
    # order has its own unique ID, instead of dropping real sales data.
    print("Fixing duplicate Order_IDs...")
    dupe_mask = df["Order_ID"].duplicated(keep="first")
    existing_nums = df["Order_ID"].str.replace("ORD", "", regex=False).astype(int)
    next_num = existing_nums.max() + 1
    new_ids = []
    for is_dupe in dupe_mask:
        if is_dupe:
            new_ids.append(f"ORD{next_num}")
            next_num += 1
        else:
            new_ids.append(None)
    df.loc[dupe_mask, "Order_ID"] = [i for i in new_ids if i is not None]

    # --- Fix 2: Missing Age ---
    # Filled with the median age so we don't distort the overall age distribution.
    print("Filling missing Age values with the median...")
    df["Age"] = df["Age"].fillna(df["Age"].median())
    df["Age"] = df["Age"].astype(int)

    # --- Fix 3: Missing City ---
    # A missing city doesn't mean we should guess a wrong one, so we
    # label it clearly instead of inventing a value.
    print("Labeling missing City values as 'Unknown'...")
    df["City"] = df["City"].fillna("Unknown")

    # --- Fix 4: Inconsistent text formatting ---
    # Trim stray spaces and make casing consistent across text columns.
    print("Cleaning up text formatting (spaces/casing)...")
    for col in ["City", "Product", "Category", "Gender"]:
        df[col] = df[col].str.strip().str.title()

    # --- Fix 5: Standardize the date column ---
    # Order_Date was stored as plain text. Converting it to an actual
    # datetime type makes it usable for any date-based analysis later.
    print("Converting Order_Date to a proper date type...")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

    # --- Fix 6: Remove fully duplicated rows (if any) ---
    before = len(df)
    df = df.drop_duplicates()
    print(f"Removed {before - len(df)} fully duplicate rows...")

    print("Cleaning complete.\n")
    return df


def add_features(df):
    """Feature engineering - new columns that make the dataset more useful
    for analysis, without changing any of the original data."""
    df = df.copy()

    print("Adding new feature columns...")

    # Group raw ages into readable age bands - useful for customer segmentation
    df["Age_Group"] = pd.cut(
        df["Age"],
        bins=[0, 25, 35, 45, 55, 100],
        labels=["18-25", "26-35", "36-45", "46-55", "56+"],
    )

    # Break the order date into separate Year / Month / Day-of-week columns,
    # since most sales analysis is done by time period
    df["Order_Year"] = df["Order_Date"].dt.year
    df["Order_Month"] = df["Order_Date"].dt.month_name()
    df["Order_Weekday"] = df["Order_Date"].dt.day_name()

    # Categorize each sale by size - handy for quickly spotting big orders
    df["Sale_Size"] = pd.cut(
        df["Total_Sales"],
        bins=[0, 50000, 150000, 300000, float("inf")],
        labels=["Small", "Medium", "Large", "Very Large"],
    )

    print("New columns added: Age_Group, Order_Year, Order_Month, Order_Weekday, Sale_Size\n")
    return df


def save_outputs(df, report_lines):
    print("Saving cleaned dataset and quality report...")
    df.to_excel(CLEAN_FILE, sheet_name="Cleaned_Sales_Data", index=False)
    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(report_lines))
    print(f"Done! Files saved:\n  - {CLEAN_FILE}\n  - {REPORT_FILE}")


if __name__ == "__main__":
    raw_df = load_data(RAW_FILE)
    report = assess_quality(raw_df)
    cleaned_df = clean_data(raw_df)
    final_df = add_features(cleaned_df)
    save_outputs(final_df, report)
