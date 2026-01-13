import matplotlib.pyplot as plt
import streamlit as st
from crud import add_customer, get_all_customers, get_pending_customers, update_customer, delete_customer
from datetime import date
from datetime import datetime
from collections import defaultdict

# ---------------- LOGIN CONFIG ----------------
VALID_USER_ID = "admin"
VALID_PASSWORD = "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

#------------------LOGIN SCREEN-------------------------------------
def login_page():
    st.markdown(
        """
        <div style="
            display:flex;
            justify-content:center;
            align-items:center;
            height:100vh;
        ">
            <div style="
                background:#ffffff;
                padding:30px;
                border-radius:16px;
                width:360px;
                box-shadow:0 10px 30px rgba(0,0,0,0.12);
            ">
                <h2 style="text-align:center;">🔐 Login</h2>
        """,
        unsafe_allow_html=True
    )

    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if user_id == VALID_USER_ID and password == VALID_PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid ID or Password")

    st.markdown("</div></div>", unsafe_allow_html=True)


if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"
#===============NAVBAR MARKDOWN===================================================================
#logut button
#if st.button("Logout"):
    #st.session_state.logged_in = False
    #st.rerun()

st.markdown("""
<style>
/* Hide Streamlit default header */
header {visibility: hidden;}

/* Navbar */
            
.top-navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 72px;
    background: linear-gradient(90deg, #1e3a8a, #1e40af);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    z-index: 9999;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.nav-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.logo-box {
    width: 42px;
    height: 42px;
    background: #ffffff;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
}

.shop-name {
    color: #ffffff;
    font-weight: 700;
    font-size: 16px;
}

.shop-address {
    color: #c7d2fe;
    font-size: 12px;
}

.nav-right {
    display: flex;
    gap: 12px;
}

.nav-right button {
    background: rgba(255,255,255,0.15);
    border: none;
    color: #ffffff;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
}

.nav-right button:hover {
    background: rgba(255,255,255,0.25);
}

</style>

<div class="top-navbar">
    <div class="nav-left">
        <div class="logo-box">🔋</div>
        <div class="shop-info">
            <div class="shop-name">GUJARAT BATTERY SERVICE</div>
            <div class="shop-address">
                Dahegam 382305, Opp. Balmukund Square • 📞 98240
            </div>
        </div>
    </div>



""", unsafe_allow_html=True)
st.markdown("<div style='height:90px'></div>", unsafe_allow_html=True)

#===============FOR BUTTONS ON DASHBOARD==========================================================
nav_cols = st.columns([1,1,1,1,1])
if nav_cols[0].button("Dashboard"):
        st.session_state.menu = "Dashboard"
if nav_cols[1].button("Add Customer"):
        st.session_state.menu = "Add Customer"
if nav_cols[2].button("Search Customer"):
        st.session_state.menu = "Search Customer"
if nav_cols[3].button("Pending Payments"):
        st.session_state.menu = "Pending Payments"
# ----- LOGIN / LOGOUT BUTTON -----
if st.session_state.logged_in:
    if nav_cols[4].button("  Logout  "):
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
           

st.markdown("""
<style>
/* ===========================
   1. GLOBAL COLORS & BACKGROUND
   =========================== */

/* Force text color everywhere */
html, body, [class*="st-"] {
    color: #111827 !important;
}

/* Page background */
.stApp {
    background-color: #eef2f7 !important;
}

/* Transparent default header/footer */
header, footer {
    background: transparent !important;
}

/* Make all headings and text same base color */
h1, h2, h3, h4, h5, h6, p, span {
    color: #111827 !important;
}

/* ===========================
   2. METRIC CARD STYLING
   =========================== */

/* Outer metric container box */
[data-testid="metric-container"] {
    background: #ffffff !important;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* All text inside metric card */
[data-testid="metric-container"] * {
    color: #111827 !important;
}

/* Metric value (big number) */
[data-testid="metric-value"] {
    font-size: 28px;
    font-weight: 700;
    color: #2563eb !important;
}

/* Metric label (title text) */
[data-testid="metric-label"] {
    font-size: 14px;
    color: #6b7280 !important;
}

/* ===========================
   3. GENERAL CARD STYLES
   =========================== */

/* Video-style card (used in some sections) */
.video-card {
    background: #ffffff !important;
    padding: 24px;
    border-radius: 12px;
    border: 1.5px solid #d0d7de !important;
    margin-bottom: 24px;
    color: #111827 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

/* Generic card classes for customers / pending payments */
.card, .customer-card, .pending-card {
    background: #ffffff !important;
    border: 1.5px solid #d0d7de !important;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

/* Remove extra borders around card containers */
div[data-testid="stVerticalBlock"] > div:has(.card) {
    border: none !important;
}

/* Extra card look (if used separately) */
.card {
    padding: 20px;
    border-radius: 12px;
    background-color: #ffffff;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
}

/* ===========================
   4. SECTION / GROUP WRAPPERS
   =========================== */

/* Big wrapper card for whole sections */
.section-wrapper {
    background: #f1f5f9;
    border-radius: 18px;
    padding: 28px;
    margin-top: 20px;
    margin-bottom: 30px;
    border: 1px solid #cbd5e1;
}

/* Box for each customer inside a section */
.customer-box {
    background: #ffffff;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 20px;
    border: 1px solid #e5e7eb;
}

/* Large section card like in the UI screenshot */
.section-card {
    background: #f1f5f9 !important;
    border: 1.5px solid #cbd5e1;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
}

/* Remove extra top-margin inside section card */
.section-card h3, 
.section-card h4, 
.section-card p {
    margin-top: 0;
}

/* ===========================
   5. INPUTS & BUTTONS
   =========================== */

/* Text, number, date, textarea inputs */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background-color: #f9fafb !important;
    border-radius: 8px !important;
    border: 1px solid #d1d5db !important;
    color: #111827 !important;
}

/* Primary buttons */
.stButton > button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    border-radius: 8px;
    padding: 10px 22px;
    font-weight: 600;
    border: none;
}

/* Button hover effect */
.stButton > button:hover {
    background-color: #1d4ed8 !important;
}

/* Text selection color */
::selection {
    background: #2563eb;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)
st.set_page_config(page_title="GUJARAT BATTERY SERVICE", layout="wide")

#---------------BLOCK APP UNTIL LOGIN---------------------------------------
if not st.session_state.logged_in:
    login_page()
    st.stop()   # ⛔ VERY IMPORTANT


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------- DASHBOARD ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if st.session_state.menu == "Dashboard":

    customers = get_all_customers()
    pending = get_pending_customers()

    total_customers = len(customers)
    pending_count = len(pending)
    monthly_sales = sum(c.get("total_amount", 0) for c in customers)

    # ===== CENTERED DASHBOARD HEADER (UPPER HEAADING OF DASHBOARD)=====
    st.markdown(
        """
        <div style="
            display:flex;
            flex-direction:column;
            align-items:center;
            margin-top:40px;
            margin-bottom:40px;
        ">
            <div style="display:flex; align-items:center; gap:12px;">
                <img src="https://img.icons8.com/color/48/battery.png" width="42"/>
                <h1 style="margin:0; font-weight:700;">GUJARAT BATTERY SERVICE</h1>
                <img src="https://img.icons8.com/color/48/battery.png" width="42"/>
            </div>
            <div style="margin-top:6px; color:#6b7280; font-size:14px;">
                Dahegam 382305 • Opp. Balmukund Square • 📞 98240
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ===== METRIC CARDS (TOTAL CUSTOMER DASHBOARD) =====
    col1, col2, col3 = st.columns([1.2, 1.2, 1.2])

    with col1:
        st.markdown(
            f"""
            <div class="video-card" style="text-align:center; padding:26px;">
                <div style="font-size:14px; color:#6b7280;">Total Customers</div>
                <div style="font-size:34px; font-weight:700; color:#2563eb;">
                    {total_customers}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="video-card" style="text-align:center; padding:26px;">
                <div style="font-size:14px; color:#6b7280;">Total Sales</div>
                <div style="font-size:34px; font-weight:700; color:#16a34a;">
                    ₹ {monthly_sales}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="video-card" style="text-align:center; padding:26px;">
                <div style="font-size:14px; color:#6b7280;">Pending Customers</div>
                <div style="font-size:34px; font-weight:700; color:#dc2626;">
                    {pending_count}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
if st.session_state.menu == "Dashboard":

    # ===== MONTHLY & YEARLY SALES DATA =====
    monthly_sales_data = defaultdict(int)
    yearly_sales_data = defaultdict(int)

    for c in customers:
        date_str = c.get("date")
        if not date_str:
            continue

        try:
            sale_date = datetime.strptime(date_str, "%Y-%m-%d")
            amount = int(c.get("total_amount", 0))

            month_key = sale_date.strftime("%b %Y")
            year_key = sale_date.strftime("%Y")

            monthly_sales_data[month_key] += amount
            yearly_sales_data[year_key] += amount
        except:
            pass

    # ===== SHOW BOTH CHARTS SIDE BY SIDE =====
    chart_col1, chart_col2 = st.columns(2)

    # ---- Monthly Sales Chart ----
   
    with chart_col1:
        if monthly_sales_data:
            months = sorted(
            monthly_sales_data.keys(),
            key=lambda x: datetime.strptime(x, "%b %Y")
        )
        values = [monthly_sales_data[m] for m in months]



        fig1 = plt.figure()
        plt.bar(months, values)
        plt.xlabel("Month")
        plt.ylabel("Sales (₹)")
        plt.title("Monthly Sales")
        plt.xticks(rotation=0
        )

        #st.markdown('<div class="video-card">', unsafe_allow_html=True)
        st.pyplot(fig1)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- Yearly Sales Chart ----
    with chart_col2:
        if yearly_sales_data:
            years = sorted(yearly_sales_data.keys())
            values = [yearly_sales_data[y] for y in years]

            fig2 = plt.figure()
            plt.bar(years, values)
            plt.xlabel("Year")
            plt.ylabel("Sales (₹)")
            plt.title("Yearly Sales")

            #st.markdown('<div class="video-card">', unsafe_allow_html=True)
            st.pyplot(fig2)
            st.markdown('</div>', unsafe_allow_html=True)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
# ---------------- ADD CUSTOMER ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if st.session_state.menu == "Add Customer":

    st.subheader("➕ Add New Customer")

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Customer Name")
            battery_name = st.text_input("Battery Name")
            serial_no = st.text_input("Serial No")
            mobile = st.text_input("Mobile Number")

        with col2:
            address = st.text_input("Address")
            brand = st.text_input("Brand")
            vehicle_no = st.text_input("Vehicle No")
            
            note = st.text_area(        #desctiption note field
                "Description / Note",
                    height=70,
                    placeholder="Warranty, old battery returned, special remarks..."
            )

        price = st.number_input("Battery Price (₹)", min_value=0)
        discount = st.number_input("Discount (₹)", min_value=0)
 
        purchase_date = st.date_input(
            "Purchase Date",
             value=date.today()
            )
        has_remaining = st.checkbox("Has Remaining Amount")

        remaining_amount = 0
        if has_remaining:
            remaining_amount = st.number_input(
                "Remaining Amount (₹)",
                min_value=0,
                step=100
            )
    
            note = st.text_area(
                "Description / Note",
            placeholder="Warranty details, old battery returned, customer remarks..."
            )

        if st.button("💾 Save Customer"):
            add_customer(
                name, mobile, address, battery_name, brand,
                serial_no, vehicle_no, price, discount,
                remaining_amount,  has_remaining,
                purchase_date.strftime("%Y-%m-%d"),note
            )
            st.success("Customer saved successfully")

        st.markdown('</div>', unsafe_allow_html=True)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------- SEARCH CUSTOMER ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

elif st.session_state.menu == "Search Customer":

    st.markdown('<div class="section-title">🔍 Search Customer</div>', unsafe_allow_html=True)

    query = st.text_input(
        "Search by Name / Mobile / Serial No",
        placeholder="Type customer name, mobile number, or serial no"
    )

    if query:
        customers = get_all_customers()

        for c in customers:
            name_val = c.get("name", "")
            mobile_val = c.get("mobile", "")
            serial_val = c.get("serial_no", "")

            if (
                query.lower() in name_val.lower()
                or query in mobile_val
                or query.lower() in serial_val.lower()
            ):

                st.markdown('<div class="video-card">', unsafe_allow_html=True)

                # --- Header row ---
                colh1, colh2 = st.columns([3, 1])
                with colh1:
                    st.markdown(f"### {name_val}")
                    st.markdown(
                        f"<span style='color:#6b7280;'>📞 {mobile_val} • 🔢 {serial_val}</span>",
                        unsafe_allow_html=True
                    )

                with colh2:
                    st.markdown(
                        f"<span style='color:#6b7280;'>📅 {c.get('date','N/A')}</span>",
                        unsafe_allow_html=True
                    )

                st.markdown("---")
                

                # --- Editable fields ---
                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input("Customer Name", name_val, key=f"name{c['id']}")
                    address = st.text_input("Address", c.get("address",""), key=f"addr{c['id']}")
                    battery = st.text_input("Battery", c.get("battery_name",""), key=f"bat{c['id']}")

                with col2:
                    brand = st.text_input("Brand", c.get("brand",""), key=f"brand{c['id']}")
                    price = st.number_input(
                        "Price",
                        value=int(c.get("price",0)),
                        key=f"price{c['id']}"
                    )
                    discount = st.number_input(
                        "Discount",
                        value=int(c.get("discount",0)),
                        key=f"disc{c['id']}"
                    )

                remaining = st.number_input(
                    "Remaining Amount",
                    value=int(c.get("remaining_amount",0)),
                    key=f"rem{c['id']}"
                )

                note_edit = st.text_area(
                    "Description / Note",
                    value=c.get("note",""),
                    key=f"note_{c['id']}",
                    height=70
                )

                total = price - discount
                st.info(f"Total Amount: ₹ {total}")

                # --- Action buttons ---
                colb1, colb2 = st.columns(2)

                with colb1:
                    if st.button("✏️ Update", key=f"upd{c['id']}"):
                        update_customer(
                            c["id"],
                            {
                                "name": name,
                                "address": address,
                                "battery_name": battery,
                                "brand": brand,
                                "price": price,
                                "discount": discount,
                                "total_amount": total,
                                "remaining_amount": remaining,
                                "has_remaining": remaining > 0,
                                "note": note_edit
                            }
                        )
                        st.success("Customer updated")

                with colb2:
                    if st.button("🗑️ Delete", key=f"del{c['id']}"):
                        delete_customer(c["id"])
                        st.error("Customer deleted")
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------- PENDING PAYMENTS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

elif st.session_state.menu == "Pending Payments":
    st.subheader("⏳ Pending Payments")
    st.markdown('<div class="section-title">⏳ Pending Payments</div>', unsafe_allow_html=True)
    pending_customers = get_pending_customers()

    if not pending_customers:
        st.success("🎉No pending payments 🎉")
    
    else:
        for c in pending_customers:

            st.markdown('<div class="video-card">', unsafe_allow_html=True)         #video card before txt

            # --- Header row ---
            colh1, colh2 = st.columns([4, 1])

            with colh1:
                st.markdown(f"### {c.get('name','')}")
                st.markdown(
                    f"<span style='color:#6b7280;'>📞 {c.get('mobile','')}</span>",
                    unsafe_allow_html=True
                )

            with colh2:
                st.markdown(
                    f"<span style='color:#dc2626; font-weight:600;'>₹ {c.get('remaining_amount',0)} due</span>",
                    unsafe_allow_html=True
                )

            st.markdown("---")

            # --- Details ---
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Battery:** {c.get('battery_name','—')}")
                st.markdown(f"**Brand:** {c.get('brand','—')}")
                st.markdown(f"**Serial No:** {c.get('serial_no','—')}")
                

            with col2:
                st.markdown(f"**Total Amount:** ₹ {c.get('total_amount',0)}")
                st.markdown(f"**Purchase Date:** {c.get('date','—')}")

            if c.get("note"):
                st.markdown(f"**Note:** {c.get('note')}")

            #st.markdown("---")         #for spacing from note - add payment textbox 

            # --- Payment input ---
            payment = st.number_input(
                "Add Payment Amount",
                min_value=0,
                max_value=int(c.get("remaining_amount", 0)),
                step=100,
                key=f"pay_{c['id']}"
            )

            # --- Action buttons ---
            b1, colb2 = st.columns(2)

            with b1:
                if st.button("➕ Add Payment", key=f"add_{c['id']}"):
                    new_remaining = c["remaining_amount"] - payment

                    update_customer(
                        c["id"],
                        {
                            "remaining_amount": new_remaining,
                            "has_remaining": new_remaining > 0
                        }
                    )

                    st.success("Payment added successfully")
                    st.rerun()

            with colb2:
                if st.button("✔ Mark as Paid", key=f"paid_{c['id']}"):
                    update_customer(
                        c["id"],
                        {
                            "remaining_amount": 0,
                            "has_remaining": False
                        }
                    )

                    st.success("Payment cleared")
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)