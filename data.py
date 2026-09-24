import streamlit as st
import pandas as pd

# ==========================================
# LOAD AND CLEAN SALES DATA
# ==========================================

@st.cache_data
def load_sales_data():

    # ------------------------------------------
    # Load CSV file
    # ------------------------------------------

    try:
        df = pd.read_csv("sales.csv")

    except FileNotFoundError:
        raise FileNotFoundError(
            "sales.csv was not found. "
            "Please make sure the file exists."
        )


    # ------------------------------------------
    # Required columns
    # ------------------------------------------

    required_columns = [
        "Date",
        "Order_ID",
        "Product",
        "Category",
        "Region",
        "Quantity",
        "Price",
        "Salesperson"
    ]


    # ------------------------------------------
    # Check required columns
    # ------------------------------------------

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing columns: "
            + ", ".join(missing_columns)
        )


    # ------------------------------------------
    # Convert data types
    # ------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce"
    )

    df["Price"] = pd.to_numeric(
        df["Price"],
        errors="coerce"
    )


    # ------------------------------------------
    # Remove invalid records
    # ------------------------------------------

    df = df.dropna(
        subset=[
            "Date",
            "Quantity",
            "Price"
        ]
    )


    # ------------------------------------------
    # Remove invalid quantities/prices
    # ------------------------------------------

    df = df[
        (df["Quantity"] > 0)
        &
        (df["Price"] >= 0)
    ]


    # ------------------------------------------
    # Calculate Revenue
    # ------------------------------------------

    df["Revenue"] = (
        df["Quantity"] * df["Price"]
    )


    # ------------------------------------------
    # Sort by Date
    # ------------------------------------------

    df = df.sort_values(
        by="Date"
    ).reset_index(
        drop=True
    )


    # ------------------------------------------
    # Return cleaned DataFrame
    # ------------------------------------------

    return df