# ============================================================
#  GUJARAT BATTERY SERVICE — v2.0
#  New Branch Edition | Light Theme | Mobile-First
# ============================================================

import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from datetime import date, datetime, timedelta
from collections import defaultdict
import json
import time

# ── PAGE CONFIG (MUST BE FIRST STREAMLIT CALL) ───────────────
st.set_page_config(
    page_title="GBS — Gajanand Battery Service",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── LAZY IMPORT (after set_page_config) ──────────────────────
from firebase_config import db
from crud import add_customer, get_all_customers, get_pending_customers, update_customer, delete_customer

# ============================================================
#  BRANCH CONFIGURATION — change for new branch
# ============================================================
BRANCH_NAME     = "🔋GBS — Dahegam"
BRANCH_ADDRESS  = "Nehru Chockdi Dahegam, Gandhinagar 382021"
BRANCH_PHONE    = "9099745456"

# ── CREDENTIALS ──────────────────────────────────────────────
APP_USERNAME = "Admin"
APP_PASSWORD = "9192"

# ── COOKIE-LIKE PERSISTENT LOGIN ─────────────────────────────
# We use st.query_params to survive page refreshes (works as long
# as the browser tab is open). True cookies need streamlit-cookies-manager
# but that requires an extra package. This approach is simple & works
# for a single-user private app used on mobile PWA.

def check_persistent_login():
    """Return True if already authenticated via query param token."""
    token = st.query_params.get("auth", "")
    return token == _make_token()

def _make_token():
    # Simple deterministic token — good enough for a private shop app
    import hashlib
    raw = f"{APP_USERNAME}:{APP_PASSWORD}:gbs_session"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]

def set_persistent_login():
    st.query_params["auth"] = _make_token()

def clear_persistent_login():
    st.query_params.pop("auth", None)

# ── SESSION STATE BOOT ────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = check_persistent_login()
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"
if "login_error" not in st.session_state:
    st.session_state.login_error = False

# ============================================================
#  GLOBAL CSS — Light Theme, Mobile-First, Clean & Professional
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], [class*="st-"] {
    font-family: 'DM Sans', sans-serif !important;
    color: #1a1f2e !important;
}

.stApp {
    background: #f0f4f9 !important;
    min-height: 100vh;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
    padding: 0 12px 100px 12px !important;
    max-width: 780px !important;
    margin: 0 auto !important;
}

/* ── TOP HEADER BAR ── */
.gbs-header {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 58px;
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    z-index: 9999;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06);
}
.gbs-header-title {
    font-size: 16px;
    font-weight: 700;
    color: #1a1f2e;
    letter-spacing: -0.3px;
}
.gbs-header-badge {
    font-size: 11px;
    background: #e8f0fe;
    color: #2563eb;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 600;
}

/* ── SPACER FOR FIXED HEADER ── */
.header-spacer { height: 68px; }

/* ── BOTTOM NAV BAR (Mobile-style) ── */
.nav-spacer { height: 72px; }

/* ── PAGE TITLE ── */
.page-title {
    font-size: 22px;
    font-weight: 700;
    color: #1a1f2e;
    margin: 18px 0 14px 0;
    letter-spacing: -0.4px;
}
.page-subtitle {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 18px;
}

/* ── CARD ── */
.gbs-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 18px 16px;
    margin-bottom: 14px;
    border: 1px solid #e9eef5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.gbs-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}
.gbs-card-name {
    font-size: 17px;
    font-weight: 700;
    color: #1a1f2e;
}
.gbs-card-meta {
    font-size: 12px;
    color: #64748b;
    margin-top: 3px;
}

/* ── METRIC CARDS ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 14px;
}
.metric-grid-2 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 14px;
}
.metric-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 14px 12px;
    text-align: center;
    border: 1px solid #e9eef5;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}
.metric-label {
    font-size: 11px;
    color: #64748b;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -1px;
    line-height: 1;
}
.metric-blue  { color: #2563eb; }
.metric-green { color: #16a34a; }
.metric-red   { color: #dc2626; }
.metric-amber { color: #d97706; }

/* ── BADGE / TAG ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
}
.badge-red    { background: #fee2e2; color: #b91c1c; }
.badge-green  { background: #dcfce7; color: #15803d; }
.badge-blue   { background: #dbeafe; color: #1d4ed8; }
.badge-amber  { background: #fef3c7; color: #b45309; }

/* ── DIVIDER ── */
.gbs-divider {
    height: 1px;
    background: #f1f5f9;
    margin: 12px 0;
}

/* ── INPUTS ── */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
.stSelectbox select {
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    color: #1a1f2e !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    transition: border-color 0.15s;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}

/* ── LABELS ── */
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stTextArea label,
.stCheckbox label,
.stRadio label,
.stSelectbox label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #374151 !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: #2563eb !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    height: 44px !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: background 0.15s, transform 0.1s !important;
    width: 100%;
}
.stButton > button:hover {
    background: #1d4ed8 !important;
    transform: translateY(-1px);
}
.stButton > button:active { transform: translateY(0); }

/* ── RADIO ── */
.stRadio [data-baseweb="radio"] { margin-right: 12px; }

/* ── SUCCESS / ERROR / INFO ── */
.stSuccess, .stError, .stInfo, .stWarning {
    border-radius: 10px !important;
    font-size: 14px !important;
}

/* ── SECTION LABEL ── */
.section-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #94a3b8;
    margin: 20px 0 10px 0;
}

/* ── BRAND HEADER ON DASHBOARD ── */
.brand-header {
    text-align: center;
    padding: 20px 0 10px 0;
}
.brand-name {
    font-size: 24px;
    font-weight: 800;
    color: #1a1f2e;
    letter-spacing: -0.8px;
}
.brand-branch {
    font-size: 13px;
    color: #64748b;
    margin-top: 4px;
}

/* ── LOGIN PAGE ── */
.login-wrapper {
    max-width: 360px;
    margin: 80px auto 0 auto;
}
.login-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 36px 28px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.09);
    border: 1px solid #e9eef5;
}
.login-logo {
    text-align: center;
    margin-bottom: 28px;
}
.login-logo-icon { font-size: 40px; margin-bottom: 8px; }
.login-logo-title {
    font-size: 20px;
    font-weight: 800;
    color: #1a1f2e;
    letter-spacing: -0.5px;
}
.login-logo-sub {
    font-size: 12px;
    color: #64748b;
    margin-top: 4px;
}

/* ── CHARTS ── */
.chart-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 16px;
    border: 1px solid #e9eef5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-bottom: 14px;
}

/* ── MOBILE RESPONSIVE ── */
@media (max-width: 600px) {
    .metric-grid { grid-template-columns: repeat(3, 1fr); gap: 8px; }
    .metric-value { font-size: 22px; }
    .metric-label { font-size: 10px; }
    .brand-name { font-size: 20px; }
    .block-container { padding: 0 8px 100px 8px !important; }
}

/* ── PENDING AMOUNT ROW ── */
.pending-amount {
    font-size: 15px;
    font-weight: 700;
    color: #dc2626;
}

/* ── BOTTOM NAV (fixed) ── */
div[data-testid="stBottom"] { display: none !important; }

/* Matplotlib chart bg */
.stpyplot { background: transparent !important; }

/* Remove top gap from columns */
div[data-testid="column"] { padding-top: 0 !important; }

/* Follow-up highlight */
.followup-due {
    background: #fff7ed;
    border: 1.5px solid #fed7aa;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #92400e;
}

/* PWA meta hint */
.pwa-hint {
    font-size: 11px;
    color: #94a3b8;
    text-align: center;
    padding: 8px;
}

/* Selectbox dropdown */
div[data-baseweb="select"] > div {
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
#  LOGIN SCREEN
# ============================================================
if not st.session_state.logged_in:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="login-card">
        <div class="login-logo">
            <div class="login-logo-icon">🔋</div>
            <div class="login-logo-title">Gajanand Battery Service</div>
            <div class="login-logo-sub">{BRANCH_NAME}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Enter username")
    password = st.text_input("Password", type="password", placeholder="Enter password")

    if st.button("🔐 Login", use_container_width=True):
        if username.strip() == APP_USERNAME and password == APP_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.login_error = False
            set_persistent_login()
            st.rerun()
        else:
            st.session_state.login_error = True

    if st.session_state.login_error:
        st.error("❌ Wrong username or password")

    st.markdown('<div class="pwa-hint">Add to Home Screen for app-like experience 📱</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ============================================================
#  HELPERS
# ============================================================

def fmt_inr(amount):
    """Format number as Indian Rupees string."""
    try:
        return f"₹ {int(amount):,}"
    except:
        return "₹ 0"

def days_ago(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        delta = (date.today() - d).days
        if delta == 0: return "Today"
        if delta == 1: return "Yesterday"
        return f"{delta}d ago"
    except:
        return date_str

def followup_status(c):
    """Return (label, is_overdue) for follow-up."""
    fu = c.get("follow_up_date")
    if not fu:
        return None, False
    try:
        fu_date = datetime.strptime(fu, "%Y-%m-%d").date()
        today = date.today()
        overdue = fu_date < today
        label = fu_date.strftime("%d %b %Y")
        return label, overdue
    except:
        return None, False

def make_chart(labels, values, title, color="#2563eb", ylabel="₹"):
    """Return a clean matplotlib figure."""
    fig, ax = plt.subplots(figsize=(5, 2.8))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")
    bars = ax.bar(labels, values, color=color, width=0.55, zorder=3)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{int(x/1000)}k" if x >= 1000 else f"₹{int(x)}"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#e2e8f0")
    ax.spines["bottom"].set_color("#e2e8f0")
    ax.tick_params(colors="#64748b", labelsize=8)
    ax.set_title(title, fontsize=11, fontweight="bold", color="#1a1f2e", pad=8)
    ax.grid(axis="y", color="#e2e8f0", linewidth=0.8, zorder=0)
    plt.xticks(rotation=30, ha="right", fontsize=8)
    plt.tight_layout(pad=1.2)
    return fig

def validate_add_form(name, mobile, price):
    """Return error string or empty string if valid."""
    if not name.strip():
        return "Customer name is required."
    if not mobile.strip() or not mobile.strip().isdigit() or len(mobile.strip()) < 10:
        return "Enter a valid 10-digit mobile number."
    if price <= 0:
        return "Battery price must be greater than ₹0."
    return ""


# ============================================================
#  FIXED HEADER
# ============================================================
st.markdown(f"""
<div class="gbs-header">
    <div class="gbs-header-title">🔋 Gajanand Battery Service</div>
    <div class="gbs-header-badge">Dahegam</div>
</div>
<div class="header-spacer"></div>
""", unsafe_allow_html=True)


# ============================================================
#  BOTTOM NAV — 5 tabs using columns
# ============================================================
nav_labels = ["📊 Home", "➕ Add", "🔍 Search", "⏳ Due", "⚙️ More"]
nav_keys   = ["Dashboard", "Add Customer", "Search Customer", "Pending Payments", "More"]

nav_cols = st.columns(5)
for i, col in enumerate(nav_cols):
    with col:
        active = st.session_state.menu == nav_keys[i]
        label = nav_labels[i]
        # Streamlit doesn't support conditional button styles easily,
        # so we show the active tab with a marker in the label
        btn_label = f"**{label}**" if active else label
        if st.button(label, key=f"nav_{i}", use_container_width=True):
            st.session_state.menu = nav_keys[i]
            st.rerun()

st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)


# ============================================================
#  DASHBOARD
# ============================================================
if st.session_state.menu == "Dashboard":

    customers = get_all_customers()
    pending   = get_pending_customers()

    total_customers  = len(customers)
    pending_count    = len(pending)
    total_revenue    = sum(c.get("total_amount", 0) for c in customers)
    total_outstanding = sum(c.get("remaining_amount", 0) for c in pending)
    car_count  = sum(1 for c in customers if c.get("battery_type","") == "🚗Car")
    bike_count = sum(1 for c in customers if c.get("battery_type","") == "🏍️Bike")

    # ── BRAND HEADER ──
    st.markdown(f"""
    <div class="brand-header">
        <div class="brand-name">Gajanand Battery Service</div>
        <div class="brand-branch">📍 {BRANCH_ADDRESS} &nbsp;•&nbsp; 📞 {BRANCH_PHONE}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── METRICS ROW 1 ──
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Customers</div>
            <div class="metric-value metric-blue">{total_customers}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Revenue</div>
            <div class="metric-value metric-green" style="font-size:18px;">₹{total_revenue:,}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Pending</div>
            <div class="metric-value metric-red">{pending_count}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── METRICS ROW 2 ──
    st.markdown(f"""
    <div class="metric-grid-2">
        <div class="metric-card">
            <div class="metric-label">🚗 Car Batteries</div>
            <div class="metric-value metric-blue">{car_count}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">🏍️ Bike Batteries</div>
            <div class="metric-value metric-green">{bike_count}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── OUTSTANDING AMOUNT ──
    if total_outstanding > 0:
        st.markdown(f"""
        <div class="gbs-card" style="border-left: 4px solid #dc2626;">
            <div style="font-size:12px; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Total Outstanding</div>
            <div style="font-size:28px; font-weight:800; color:#dc2626; margin-top:4px;">₹ {total_outstanding:,}</div>
            <div style="font-size:12px; color:#94a3b8; margin-top:4px;">Across {pending_count} customers</div>
        </div>
        """, unsafe_allow_html=True)

    # ── FOLLOW-UPS DUE TODAY ──
    today = date.today()
    followups_today = []
    for c in customers:
        fu = c.get("follow_up_date")
        if fu:
            try:
                fu_date = datetime.strptime(fu, "%Y-%m-%d").date()
                if fu_date <= today:
                    followups_today.append(c)
            except:
                pass

    if followups_today:
        st.markdown('<div class="section-label">🔔 Follow-ups Due</div>', unsafe_allow_html=True)
        for c in followups_today:
            fu_label, is_overdue = followup_status(c)
            st.markdown(f"""
            <div class="followup-due">
                <strong>{c.get('name','')}</strong> &nbsp;
                <span style="opacity:0.7;">📞 {c.get('mobile','')}</span><br>
                📅 Follow-up: {fu_label} &nbsp;
                {'<span class="badge badge-red">Overdue</span>' if is_overdue else '<span class="badge badge-amber">Due Today</span>'}
                {f"<br><span style='font-size:12px;'>{c.get('follow_up_note','')}</span>" if c.get('follow_up_note') else ''}
            </div>
            """, unsafe_allow_html=True)

    # ── CHARTS ──
    monthly_data = defaultdict(int)
    yearly_data  = defaultdict(int)

    for c in customers:
        date_str = c.get("date","")
        if not date_str:
            continue
        try:
            sale_date = datetime.strptime(date_str, "%Y-%m-%d")
            amount    = int(c.get("total_amount", 0))
            monthly_data[sale_date.strftime("%b %Y")] += amount
            yearly_data[sale_date.strftime("%Y")]     += amount
        except:
            pass

    st.markdown('<div class="section-label">📈 Sales Analytics</div>', unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)

    with ch1:
        if monthly_data:
            months = sorted(monthly_data.keys(), key=lambda x: datetime.strptime(x, "%b %Y"))
            values = [monthly_data[m] for m in months]
            fig = make_chart(months, values, "Monthly Sales", color="#2563eb")
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.markdown('</div>', unsafe_allow_html=True)

    with ch2:
        if yearly_data:
            years  = sorted(yearly_data.keys())
            values = [yearly_data[y] for y in years]
            fig = make_chart(years, values, "Yearly Sales", color="#16a34a")
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── RECENT CUSTOMERS ──
    st.markdown('<div class="section-label">👥 Recent Customers</div>', unsafe_allow_html=True)
    sorted_customers = sorted(
        customers,
        key=lambda x: x.get("date", ""), reverse=True
    )
    for c in sorted_customers[:5]:
        remaining = c.get("remaining_amount", 0)
        st.markdown(f"""
        <div class="gbs-card" style="padding:14px 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:15px; font-weight:700;">{c.get('name','')}</div>
                    <div style="font-size:12px; color:#64748b;">📞 {c.get('mobile','')} • {c.get('battery_type','')}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:14px; font-weight:600; color:#16a34a;">{fmt_inr(c.get('total_amount',0))}</div>
                    <div style="font-size:11px; color:#94a3b8;">{days_ago(c.get('date',''))}</div>
                </div>
            </div>
            {f'<div style="margin-top:8px;"><span class="badge badge-red">Due: {fmt_inr(remaining)}</span></div>' if remaining > 0 else ''}
        </div>
        """, unsafe_allow_html=True)


# ============================================================
#  ADD CUSTOMER
# ============================================================
elif st.session_state.menu == "Add Customer":

    st.markdown('<div class="page-title">➕ New Customer</div>', unsafe_allow_html=True)
    st.markdown('<div class="gbs-card">', unsafe_allow_html=True)

    battery_type = st.radio("Battery Type", ["🚗Car", "🏍️Bike"], horizontal=True)

    st.markdown('<div class="section-label">Customer Details</div>', unsafe_allow_html=True)
    name    = st.text_input("Customer Name *", placeholder="Full name")
    mobile  = st.text_input("Mobile Number *", placeholder="10-digit number")
    address = st.text_input("Address", placeholder="Village / Area")

    st.markdown('<div class="section-label">Battery Details</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        battery_name = st.text_input("Battery Name", placeholder="e.g. 35AH")
        serial_no    = st.text_input("Serial No", placeholder="Serial number")
    with c2:
        brand      = st.text_input("Brand", placeholder="e.g. Amaron, Exide")
        vehicle_no = st.text_input("Vehicle No", placeholder="GJ-XX-XXXX")

    st.markdown('<div class="section-label">Pricing</div>', unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    with p1:
        price    = st.number_input("Battery Price (₹) *", min_value=0, step=100)
    with p2:
        discount = st.number_input("Discount (₹)", min_value=0, step=50)

    total_display = price - discount
    if price > 0:
        st.markdown(f"""
        <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:10px; padding:10px 14px; margin:4px 0 12px 0;">
            <span style="font-size:13px; color:#0369a1; font-weight:600;">Total: ₹ {total_display:,}</span>
            {f'<span style="font-size:12px; color:#16a34a; margin-left:12px;">Discount: ₹ {discount:,}</span>' if discount > 0 else ''}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Date & Notes</div>', unsafe_allow_html=True)
    purchase_date = st.date_input("Purchase Date", value=date.today())
    note = st.text_area("Note", height=70, placeholder="Warranty, condition, old battery details...")

    st.markdown('<div class="section-label">Payment</div>', unsafe_allow_html=True)
    has_remaining   = st.checkbox("Has Remaining Amount")
    remaining_amount = 0
    payment_note     = ""

    if has_remaining:
        remaining_amount = st.number_input("Remaining Amount (₹)", min_value=0, step=100)
        payment_note     = st.text_area("Payment Note", height=60, placeholder="Promised date, installment plan...")

    # Follow-up scheduling
    st.markdown('<div class="section-label">📅 Follow-up (Optional)</div>', unsafe_allow_html=True)
    set_followup = st.checkbox("Schedule a Follow-up")
    follow_up_date_val = None
    follow_up_note_val = ""
    if set_followup:
        fu_col1, fu_col2 = st.columns(2)
        with fu_col1:
            fu_date = st.date_input("Follow-up Date", value=date.today() + timedelta(days=30))
            follow_up_date_val = fu_date.strftime("%Y-%m-%d")
        with fu_col2:
            follow_up_note_val = st.text_input("Follow-up Reason", placeholder="Battery check, warranty claim...")

    if st.button("💾 Save Customer", use_container_width=True):
        err = validate_add_form(name, mobile, price)
        if err:
            st.error(f"❌ {err}")
        else:
            add_customer(
                name.strip(), mobile.strip(), address.strip(),
                battery_type, battery_name.strip(), brand.strip(),
                serial_no.strip(), vehicle_no.strip(),
                price, discount, remaining_amount,
                has_remaining, purchase_date.strftime("%Y-%m-%d"),
                note.strip(), payment_note.strip()
            )
            # Update follow-up if set
            # (add_customer doesn't support it directly, so we patch via get + update)
            if set_followup and follow_up_date_val:
                all_c = get_all_customers()
                # Find the customer we just added (latest by created_at)
                latest = sorted(all_c, key=lambda x: x.get("created_at", datetime.min), reverse=True)
                if latest:
                    update_customer(latest[0]["id"], {
                        "follow_up_date": follow_up_date_val,
                        "follow_up_note": follow_up_note_val
                    })
            st.success("✅ Customer saved successfully!")
            time.sleep(0.5)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
#  SEARCH CUSTOMER
# ============================================================
elif st.session_state.menu == "Search Customer":

    st.markdown('<div class="page-title">🔍 Search Customer</div>', unsafe_allow_html=True)

    query = st.text_input("", placeholder="Search by name, mobile, serial no, vehicle no...")

    if query and len(query.strip()) >= 2:
        customers = get_all_customers()
        q = query.strip().lower()

        results = [
            c for c in customers
            if q in c.get("name","").lower()
            or q in c.get("mobile","")
            or q in c.get("serial_no","").lower()
            or q in c.get("vehicle_no","").lower()
        ]

        if not results:
            st.info("No customers found.")
        else:
            st.markdown(f'<div class="page-subtitle">{len(results)} result(s) found</div>', unsafe_allow_html=True)

        for c in results:
            remaining = c.get("remaining_amount", 0)
            fu_label, fu_overdue = followup_status(c)

            with st.expander(
                f"{'🔴' if remaining > 0 else '🟢'} {c.get('name','')} — {c.get('mobile','')}",
                expanded=False
            ):
                # ── READ-ONLY SUMMARY ──
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**🔋 Battery:** {c.get('battery_name','—')} ({c.get('brand','—')})")
                    st.markdown(f"**🔢 Serial:** {c.get('serial_no','—')}")
                    st.markdown(f"**🚘 Vehicle:** {c.get('vehicle_no','—')}")
                with col2:
                    st.markdown(f"**💰 Total:** {fmt_inr(c.get('total_amount',0))}")
                    st.markdown(f"**📅 Date:** {c.get('date','—')}")
                    if remaining > 0:
                        st.markdown(f"**⚠️ Due:** {fmt_inr(remaining)}")

                if c.get("note"):
                    st.markdown(f"**📝 Note:** {c.get('note')}")
                if fu_label:
                    badge = '🔴 Overdue' if fu_overdue else '🟡 Scheduled'
                    st.markdown(f"**📅 Follow-up:** {fu_label} {badge}")
                    if c.get("follow_up_note"):
                        st.markdown(f"**Reason:** {c.get('follow_up_note')}")

                st.markdown('<div class="gbs-divider"></div>', unsafe_allow_html=True)
                st.markdown("**✏️ Edit**")

                # ── EDITABLE FIELDS ──
                e1, e2 = st.columns(2)
                with e1:
                    e_name    = st.text_input("Name",    c.get("name",""),         key=f"en_{c['id']}")
                    e_mobile  = st.text_input("Mobile",  c.get("mobile",""),       key=f"em_{c['id']}")
                    e_battery = st.text_input("Battery", c.get("battery_name",""), key=f"eb_{c['id']}")
                    e_brand   = st.text_input("Brand",   c.get("brand",""),        key=f"ebr_{c['id']}")
                with e2:
                    e_serial  = st.text_input("Serial No", c.get("serial_no",""),  key=f"es_{c['id']}")
                    e_vehicle = st.text_input("Vehicle No",c.get("vehicle_no",""), key=f"ev_{c['id']}")
                    e_price   = st.number_input("Price",   int(c.get("price",0)),   key=f"ep_{c['id']}")
                    e_disc    = st.number_input("Discount", int(c.get("discount",0)),key=f"ed_{c['id']}")

                e_remaining = st.number_input("Remaining (₹)", int(c.get("remaining_amount",0)), key=f"er_{c['id']}")
                e_note      = st.text_area("Note", c.get("note",""), height=70, key=f"enote_{c['id']}")

                # Follow-up edit
                e_fu_date = st.text_input("Follow-up Date (YYYY-MM-DD)", c.get("follow_up_date",""), key=f"efu_{c['id']}")
                e_fu_note = st.text_input("Follow-up Reason", c.get("follow_up_note",""), key=f"efun_{c['id']}")

                e_total = e_price - e_disc
                st.markdown(f'<div style="font-size:13px; color:#2563eb; font-weight:600; margin:4px 0 10px 0;">Total: ₹ {e_total:,}</div>', unsafe_allow_html=True)

                eb1, eb2 = st.columns(2)
                with eb1:
                    if st.button("✏️ Update", key=f"upd_{c['id']}", use_container_width=True):
                        update_customer(c["id"], {
                            "name": e_name.strip(),
                            "mobile": e_mobile.strip(),
                            "battery_name": e_battery.strip(),
                            "brand": e_brand.strip(),
                            "serial_no": e_serial.strip(),
                            "vehicle_no": e_vehicle.strip(),
                            "price": e_price,
                            "discount": e_disc,
                            "total_amount": e_total,
                            "remaining_amount": e_remaining,
                            "has_remaining": e_remaining > 0,
                            "note": e_note.strip(),
                            "follow_up_date": e_fu_date.strip() or None,
                            "follow_up_note": e_fu_note.strip(),
                        })
                        st.success("✅ Updated")
                        st.rerun()
                with eb2:
                    if st.button("🗑️ Delete", key=f"del_{c['id']}", use_container_width=True):
                        delete_customer(c["id"])
                        st.error("Deleted")
                        st.rerun()
    elif query and len(query.strip()) < 2:
        st.markdown('<div style="color:#94a3b8; font-size:13px;">Type at least 2 characters...</div>', unsafe_allow_html=True)


# ============================================================
#  PENDING PAYMENTS
# ============================================================
elif st.session_state.menu == "Pending Payments":

    pending = get_pending_customers()
    total_due = sum(c.get("remaining_amount", 0) for c in pending)

    st.markdown('<div class="page-title">⏳ Pending Payments</div>', unsafe_allow_html=True)

    if not pending:
        st.success("🎉 All payments cleared! No pending dues.")
    else:
        st.markdown(f"""
        <div class="gbs-card" style="border-left:4px solid #dc2626; margin-bottom:16px;">
            <div style="font-size:12px; color:#64748b; font-weight:600; text-transform:uppercase;">Total Outstanding</div>
            <div style="font-size:26px; font-weight:800; color:#dc2626;">₹ {total_due:,}</div>
            <div style="font-size:12px; color:#94a3b8;">{len(pending)} customers pending</div>
        </div>
        """, unsafe_allow_html=True)

        # Sort by remaining amount (highest first)
        pending_sorted = sorted(pending, key=lambda x: x.get("remaining_amount", 0), reverse=True)

        for c in pending_sorted:
            rem    = c.get("remaining_amount", 0)
            total  = c.get("total_amount", 0)
            paid   = total - rem
            pct    = int((paid / total * 100)) if total > 0 else 0
            fu_label, fu_overdue = followup_status(c)

            st.markdown(f"""
            <div class="gbs-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div class="gbs-card-name">{c.get('name','')}</div>
                        <div class="gbs-card-meta">📞 {c.get('mobile','')} &nbsp;•&nbsp; {c.get('battery_type','')}</div>
                        <div class="gbs-card-meta">📅 {c.get('date','—')} &nbsp;•&nbsp; {c.get('battery_name','—')}</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="pending-amount">₹ {rem:,} due</div>
                        <div style="font-size:11px; color:#94a3b8;">of ₹ {total:,} total</div>
                    </div>
                </div>
                <div style="background:#f1f5f9; border-radius:6px; height:6px; margin:10px 0 6px 0; overflow:hidden;">
                    <div style="background:#16a34a; width:{pct}%; height:100%; border-radius:6px;"></div>
                </div>
                <div style="font-size:11px; color:#94a3b8; margin-bottom:8px;">Paid: {pct}% (₹ {paid:,})</div>
                {f'<div style="font-size:12px; color:#92400e; margin-bottom:6px;">📅 Follow-up: {fu_label} {"🔴" if fu_overdue else "🟡"}</div>' if fu_label else ''}
                {f'<div style="font-size:12px; color:#64748b; margin-bottom:8px;">💬 {c.get("payment_note","")}</div>' if c.get("payment_note") else ''}
            </div>
            """, unsafe_allow_html=True)

            # Payment input
            payment = st.number_input(
                f"Add payment for {c.get('name','')}",
                min_value=0, max_value=int(rem), step=100,
                key=f"pay_{c['id']}"
            )

            pb1, pb2 = st.columns(2)
            with pb1:
                if st.button("➕ Add Payment", key=f"addpay_{c['id']}", use_container_width=True):
                    if payment <= 0:
                        st.warning("Enter a payment amount.")
                    else:
                        new_rem = rem - payment
                        update_customer(c["id"], {
                            "remaining_amount": new_rem,
                            "has_remaining": new_rem > 0
                        })
                        st.success(f"✅ ₹{payment:,} added. Remaining: ₹{new_rem:,}")
                        st.rerun()
            with pb2:
                if st.button("✔ Mark Paid", key=f"markpaid_{c['id']}", use_container_width=True):
                    update_customer(c["id"], {
                        "remaining_amount": 0,
                        "has_remaining": False
                    })
                    st.success("✅ Payment cleared")
                    st.rerun()

            st.markdown('<div class="gbs-divider"></div>', unsafe_allow_html=True)


# ============================================================
#  MORE (Settings / Export / Logout)
# ============================================================
elif st.session_state.menu == "More":

    st.markdown('<div class="page-title">⚙️ More</div>', unsafe_allow_html=True)

    # ── BRANCH INFO ──
    st.markdown(f"""
    <div class="gbs-card">
        <div style="font-size:12px; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px;">Branch Info</div>
        <div style="font-size:15px; font-weight:700;">🔋 Gujarat Battery Service</div>
        <div style="font-size:13px; color:#64748b; margin-top:4px;">📍 {BRANCH_ADDRESS}</div>
        <div style="font-size:13px; color:#64748b; margin-top:2px;">📞 {BRANCH_PHONE}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── EXPORT TO CSV ──
    st.markdown('<div class="section-label">📥 Export Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="gbs-card">', unsafe_allow_html=True)
    if st.button("📥 Export All Customers to CSV", use_container_width=True):
        customers = get_all_customers()
        if customers:
            df = pd.DataFrame(customers)
            # Drop internal fields for clean export
            for col in ["id", "created_at", "follow_up_date", "follow_up_note"]:
                if col in df.columns:
                    df = df.drop(columns=[col])
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download CSV",
                data=csv,
                file_name=f"gbs_customers_{date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No customer data to export.")

    if st.button("📥 Export Pending Payments to CSV", use_container_width=True):
        pending = get_pending_customers()
        if pending:
            df = pd.DataFrame(pending)
            for col in ["id", "created_at"]:
                if col in df.columns:
                    df = df.drop(columns=[col])
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Pending CSV",
                data=csv,
                file_name=f"gbs_pending_{date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No pending payments.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── QUICK STATS ──
    st.markdown('<div class="section-label">📊 Quick Stats</div>', unsafe_allow_html=True)
    customers = get_all_customers()
    if customers:
        brands = defaultdict(int)
        battery_types = defaultdict(int)
        for c in customers:
            b = c.get("brand","Unknown").strip()
            t = c.get("battery_type","Unknown")
            if b: brands[b] += 1
            if t: battery_types[t] += 1

        top_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5]
        st.markdown('<div class="gbs-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px; font-weight:600; color:#374151; margin-bottom:10px;">Top Brands</div>', unsafe_allow_html=True)
        for brand_name, cnt in top_brands:
            pct = int(cnt / len(customers) * 100)
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; margin-bottom:6px; font-size:13px;">
                <span>{brand_name}</span>
                <span style="color:#2563eb; font-weight:600;">{cnt} ({pct}%)</span>
            </div>
            <div style="background:#f1f5f9; border-radius:4px; height:4px; margin-bottom:10px;">
                <div style="background:#2563eb; width:{pct}%; height:100%; border-radius:4px;"></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── PWA INSTALL HINT ──
    st.markdown("""
    <div class="gbs-card" style="border:1px dashed #cbd5e1;">
        <div style="font-size:13px; font-weight:700; color:#374151; margin-bottom:6px;">📱 Install as App</div>
        <div style="font-size:12px; color:#64748b;">
            On mobile: Open in browser → tap Share / Menu → <b>Add to Home Screen</b><br><br>
            This works on both iOS (Safari) and Android (Chrome). The app will open fullscreen like a native app.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── LOGOUT ──
    st.markdown('<div class="section-label">Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="gbs-card">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:13px; color:#64748b; margin-bottom:12px;">Logged in as <strong>{APP_USERNAME}</strong></div>', unsafe_allow_html=True)
    if st.button("🔓 Logout", use_container_width=True):
        st.session_state.logged_in = False
        clear_persistent_login()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
