
import streamlit as st
import pandas as pd
import sqlite3

# Database Connection
conn = sqlite3.connect("pharmacy.db", check_same_thread=False)
cursor = conn.cursor()

# Create Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS medicines(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    quantity INTEGER,
    price REAL,
    expiry_date TEXT
)
""")
conn.commit()

st.set_page_config(page_title="Pharmacy Management System")

st.title("💊 Pharmacy Management System")

menu = st.sidebar.selectbox(
    "Select Menu",
    [
        "Dashboard",
        "Add Medicine",
        "View Medicines",
        "Search Medicine"
    ]
)

if menu == "Dashboard":

    st.header("Dashboard")

    df = pd.read_sql_query(
        "SELECT * FROM medicines",
        conn
    )

    st.metric("Total Medicines", len(df))

    if len(df) > 0:

        low_stock = df[df["quantity"] < 10]

        st.subheader("Low Stock Medicines")

        if len(low_stock) > 0:
            st.dataframe(low_stock)
        else:
            st.success("No Low Stock Medicines")

        st.subheader("AI Stock Recommendation")

        for _, row in low_stock.iterrows():
            st.warning(
                f"Restock {row['name']} immediately"
            )

elif menu == "Add Medicine":

    st.header("Add Medicine")

    name = st.text_input("Medicine Name")

    quantity = st.number_input(
        "Quantity",
        min_value=0
    )

    price = st.number_input(
        "Price",
        min_value=0.0
    )

    expiry = st.date_input(
        "Expiry Date"
    )

    if st.button("Add Medicine"):

        cursor.execute(
            """
            INSERT INTO medicines
            (name, quantity, price, expiry_date)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                quantity,
                price,
                str(expiry)
            )
        )

        conn.commit()

        st.success("Medicine Added Successfully")

elif menu == "View Medicines":

    st.header("Inventory")

    df = pd.read_sql_query("SELECT * FROM medicines", conn)

    if len(df) == 0:
        st.info("No medicines found")
    else:

        # TABLE HEADER (IMPORTANT - keeps heading row)
        header_cols = st.columns([1, 3, 2, 2, 2, 3])
        header_cols[0].write("ID")
        header_cols[1].write("Name")
        header_cols[2].write("Quantity")
        header_cols[3].write("Price")
        header_cols[4].write("Expiry")
        header_cols[5].write("Actions")

        # TABLE ROWS
        for i, row in df.iterrows():

            cols = st.columns([1, 3, 2, 2, 2, 3])

            cols[0].write(row["id"])
            cols[1].write(row["name"])
            cols[2].write(row["quantity"])
            cols[3].write(row["price"])
            cols[4].write(row["expiry_date"])

            # DELETE BUTTON
            if cols[5].button("🗑 Delete", key=f"del_{row['id']}"):

                cursor.execute(
                    "DELETE FROM medicines WHERE id=?",
                    (row["id"],)
                )
                conn.commit()

                st.success(f"{row['name']} deleted successfully")
                st.rerun()

elif menu == "Search Medicine":

    st.header("Search Medicine")

    search = st.text_input(
        "Enter Medicine Name"
    )

    if search:

        query = f"""
        SELECT * FROM medicines
        WHERE name LIKE '%{search}%'
        """

        df = pd.read_sql_query(
            query,
            conn
        )

        st.dataframe(df)
