
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

    df = pd.read_sql_query(
        "SELECT * FROM medicines",
        conn
    )

    # Keep header row (Streamlit table)
    st.dataframe(df, use_container_width=True)

    st.markdown("### Manage Medicines")

    for i, row in df.iterrows():

        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 3])

        with col1:
            st.write(row["id"])

        with col2:
            st.write(row["name"])

        with col3:
            st.write(row["quantity"])

        with col4:
            st.write(row["price"])

        with col5:

            btn1, btn2 = st.columns(2)

            # EDIT BUTTON
            with btn1:
                if st.button("✏️ Edit", key=f"edit_{row['id']}"):

                    st.session_state["edit_id"] = row["id"]
                    st.session_state["edit_name"] = row["name"]
                    st.session_state["edit_qty"] = row["quantity"]
                    st.session_state["edit_price"] = row["price"]
                    st.session_state["edit_expiry"] = row["expiry_date"]

            # DELETE BUTTON
            with btn2:
                if st.button("🗑 Delete", key=f"delete_{row['id']}"):

                    cursor.execute(
                        "DELETE FROM medicines WHERE id=?",
                        (row["id"],)
                    )
                    conn.commit()
                    st.success(f"{row['name']} deleted successfully")
                    st.rerun()
if "edit_id" in st.session_state:

    st.markdown("## Edit Medicine")

    name = st.text_input("Name", st.session_state["edit_name"])
    qty = st.number_input("Quantity", value=st.session_state["edit_qty"])
    price = st.number_input("Price", value=st.session_state["edit_price"])
    expiry = st.date_input("Expiry Date")

    if st.button("Update Medicine"):

        cursor.execute("""
            UPDATE medicines
            SET name=?, quantity=?, price=?, expiry_date=?
            WHERE id=?
        """, (name, qty, price, str(expiry), st.session_state["edit_id"]))

        conn.commit()

        st.success("Medicine updated successfully")

        del st.session_state["edit_id"]
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
