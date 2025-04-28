import streamlit as st
import pandas as pd
import difflib

import streamlit as st
import pandas as pd
import difflib

st.set_page_config(page_title="🚀 Sales KPI Dashboard", layout="centered", page_icon="📊")

st.markdown(
    """
    <style>
        body { background-color: #0b0c10; color: #c5c6c7; }
        .stApp { background: linear-gradient(135deg, #0b0c10, #66fcf1); }
        .title { color: #66fcf1; font-size: 40px; text-align: center; }
        .subheader { color: #45a29e; font-size: 25px; text-align: center; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="title">🛸 Sales KPI Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="subheader">Upload your file and let the stars align with insights...</h3>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("🚀 Upload your sales data", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')  
        elif uploaded_file.name.endswith("xlsx"):
            df = pd.read_excel(uploaded_file, engine='openpyxl')  
    except Exception as e:
        st.error(f"Error reading file: {e}")


    df.columns = df.columns.str.strip()

    st.write("Column names in the data:")
    st.write(df.columns)

    def match_column(possible_names, user_columns):
        best_match = None
        for col in user_columns:
            match = difflib.get_close_matches(col.lower(), possible_names, cutoff=0.6)
            if match:
                best_match = match[0]
                break
        return best_match

    price_col = match_column(["price", "unit_price", "priceeach", "amount"], df.columns.str.lower().tolist())
    qty_col = match_column(["qty", "quantity", "units_sold"], df.columns.str.lower().tolist())
    date_col = match_column(["date", "purchase_date", "transaction_date"], df.columns.str.lower().tolist())
    rep_col = match_column(["sales rep", "salesperson", "rep"], df.columns.str.lower().tolist())
    region_col = match_column(["region", "territory", "area"], df.columns.str.lower().tolist())

    missing_columns = []
    if not price_col:
        missing_columns.append("Price")
    if not qty_col:
        missing_columns.append("Quantity")
    if not date_col:
        missing_columns.append("Date")
    if not rep_col:
        missing_columns.append("Sales Rep")
    if not region_col:
        missing_columns.append("Region")

    if missing_columns:
        st.warning(f"Missing columns: {', '.join(missing_columns)}. The analysis will continue with available data.")

    if price_col and qty_col:
        if price_col in df.columns and qty_col in df.columns:
            df["Total"] = df[price_col] * df[qty_col]  
        else:
            st.warning("Price and/or Quantity columns not found in the dataset. Cannot calculate 'Total'.")
    else:
        st.warning("Could not calculate 'Total' as 'Price' or 'Quantity' column is missing.")

    if "Total" in df:
        total_revenue = df["Total"].sum()
        avg_deal_size = df["Total"].mean()
        total_orders = len(df)

        st.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
        st.metric("📦 Average Deal Size", f"${avg_deal_size:,.2f}")
        st.metric("📊 Total Orders", f"{total_orders}")
    else:
        st.warning("Cannot calculate KPI metrics because 'Total' is unavailable.")

    if rep_col:
        try:
            sales_by_rep = df.groupby(rep_col)["Total"].sum().sort_values()
            st.write("Sales by Sales Rep:")
            st.bar_chart(sales_by_rep)
        except KeyError:
            st.warning(f"Column '{rep_col}' not found in the dataset.")

    if date_col:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')  
            monthly_sales = df.groupby(df[date_col].dt.to_period("M"))["Total"].sum()
            st.write("Monthly Sales Trend:")
            st.line_chart(monthly_sales)
        except KeyError:
            st.warning(f"Column '{date_col}' not found in the dataset.")
        
    if region_col:
        try:
            sales_by_region = df.groupby(region_col)["Total"].sum()
            st.write("Sales by Region:")
            st.bar_chart(sales_by_region)
        except KeyError:
            st.warning(f"Column '{region_col}' not found in the dataset.")
