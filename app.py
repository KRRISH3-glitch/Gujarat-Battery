# ============================================================
#  GUJARAT BATTERY SERVICE — v2.1
#  Fix: Search card overlap | New: QR/Barcode Scanner
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from datetime import date, datetime, timedelta
from collections import defaultdict
import time

# ── PAGE CONFIG (MUST BE FIRST) ──────────────────────────────
st.set_page_config(
    page_title="GB — Gajanand Battery",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from firebase_config import db
from crud import add_customer, get_all_customers, get_pending_customers, update_customer, delete_customer

# ============================================================
#  BRANCH CONFIG
# ============================================================
BRANCH_NAME    = "GB — Gandhinagar Branch"
BRANCH_ADDRESS = "Nehru CHockdi, Gandhinagar"
BRANCH_PHONE   = "9099745456"

APP_USERNAME = "Admin"
APP_PASSWORD = "9192"

# ── PERSISTENT LOGIN ─────────────────────────────────────────
def _make_token():
    import hashlib
    raw = f"{APP_USERNAME}:{APP_PASSWORD}:gbs_session"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]

def check_persistent_login():
    return st.query_params.get("auth", "") == _make_token()

def set_persistent_login():
    st.query_params["auth"] = _make_token()

def clear_persistent_login():
    st.query_params.pop("auth", None)

# ── SESSION STATE ─────────────────────────────────────────────
if "logged_in"      not in st.session_state: st.session_state.logged_in      = check_persistent_login()
if "menu"           not in st.session_state: st.session_state.menu           = "Dashboard"
if "login_error"    not in st.session_state: st.session_state.login_error    = False
if "scanned_serial" not in st.session_state: st.session_state.scanned_serial = ""
if "scan_mode"      not in st.session_state: st.session_state.scan_mode      = None  # "add" | "search" | None

# ── Pick up scanned serial from URL query param ──────────────
_scanned_from_url = st.query_params.get("scanned", "")
if _scanned_from_url and _scanned_from_url != st.session_state.scanned_serial:
    st.session_state.scanned_serial = _scanned_from_url
    st.query_params.pop("scanned", None)

# ============================================================
#  GLOBAL CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], [class*="st-"] {
    font-family: 'DM Sans', sans-serif !important;
    color: #1a1f2e !important;
}
.stApp { background: #f0f4f9 !important; }
#MainMenu, footer, header { visibility: hidden !important; }

.block-container {
    padding: 0 12px 110px 12px !important;
    max-width: 800px !important;
    margin: 0 auto !important;
}

/* ── TOP HEADER ── */
.gbs-header {
    position: fixed; top:0; left:0; right:0;
    height: 56px;
    background: #fff;
    border-bottom: 1px solid #e2e8f0;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 16px;
    z-index: 9999;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.gbs-header-title { font-size:16px; font-weight:800; color:#1a1f2e; letter-spacing:-0.3px; }
.gbs-header-badge {
    font-size:11px; background:#e8f0fe; color:#2563eb;
    padding:3px 10px; border-radius:20px; font-weight:700;
}
.header-spacer { height: 66px; }

/* ── CARDS ── */
.gbs-card {
    background:#fff; border-radius:16px; padding:16px;
    margin-bottom:12px; border:1px solid #e9eef5;
    box-shadow:0 2px 8px rgba(0,0,0,0.04);
}

/* ── CUSTOMER RESULT CARD ── */
.cust-card {
    background:#fff; border-radius:14px;
    border:1px solid #e2e8f0;
    margin-bottom:4px;
    box-shadow:0 2px 6px rgba(0,0,0,0.04);
    overflow:hidden;
}
.cust-card-header {
    display:flex; justify-content:space-between; align-items:center;
    padding:13px 16px;
}
.cust-card-name {
    font-size:16px; font-weight:700; color:#1a1f2e;
    line-height:1.3;
}
.cust-card-sub { font-size:12px; color:#64748b; margin-top:2px; }
.cust-card-right { text-align:right; flex-shrink:0; padding-left:10px; }

/* ── METRIC GRIDS ── */
.metric-grid   { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:12px; }
.metric-grid-2 { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin-bottom:12px; }
.metric-card {
    background:#fff; border-radius:14px; padding:13px 10px;
    text-align:center; border:1px solid #e9eef5;
    box-shadow:0 2px 6px rgba(0,0,0,0.04);
}
.metric-label { font-size:10px; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:5px; }
.metric-value { font-size:25px; font-weight:800; letter-spacing:-1px; line-height:1; }
.c-blue  { color:#2563eb; } .c-green { color:#16a34a; }
.c-red   { color:#dc2626; } .c-amber { color:#d97706; }

/* ── BADGE ── */
.badge { display:inline-block; padding:2px 9px; border-radius:20px; font-size:11px; font-weight:700; }
.badge-red   { background:#fee2e2; color:#b91c1c; }
.badge-green { background:#dcfce7; color:#15803d; }
.badge-blue  { background:#dbeafe; color:#1d4ed8; }
.badge-amber { background:#fef3c7; color:#b45309; }

/* ── SECTION LABEL ── */
.section-label {
    font-size:11px; font-weight:700; text-transform:uppercase;
    letter-spacing:0.8px; color:#94a3b8; margin:18px 0 8px 0;
}
.page-title { font-size:22px; font-weight:800; color:#1a1f2e; margin:16px 0 12px 0; letter-spacing:-0.5px; }

/* ── INPUTS ── */
.stTextInput input, .stNumberInput input,
.stDateInput input, .stTextArea textarea {
    background:#f8fafc !important; border:1.5px solid #e2e8f0 !important;
    border-radius:10px !important; color:#1a1f2e !important;
    font-family:'DM Sans',sans-serif !important; font-size:14px !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color:#2563eb !important;
    box-shadow:0 0 0 3px rgba(37,99,235,0.10) !important;
}
.stTextInput label, .stNumberInput label, .stDateInput label,
.stTextArea label, .stCheckbox label, .stRadio label {
    font-size:13px !important; font-weight:600 !important; color:#374151 !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background:#2563eb !important; color:#fff !important;
    border:none !important; border-radius:10px !important;
    font-weight:700 !important; font-size:14px !important;
    height:44px !important; font-family:'DM Sans',sans-serif !important;
    transition:background 0.15s !important; width:100%;
}
.stButton > button:hover { background:#1d4ed8 !important; }

/* ── SCAN BUTTON (amber) ── */
.scan-btn > div > button,
.scan-btn .stButton > button { background:#f59e0b !important; }
.scan-btn > div > button:hover,
.scan-btn .stButton > button:hover { background:#d97706 !important; }

/* ── DIVIDER ── */
.gbs-divider { height:1px; background:#f1f5f9; margin:12px 0; }

/* ── BRAND HEADER ── */
.brand-header { text-align:center; padding:16px 0 8px 0; }
.brand-name { font-size:22px; font-weight:800; color:#1a1f2e; letter-spacing:-0.8px; }
.brand-branch { font-size:12px; color:#64748b; margin-top:4px; }

/* ── CHART CARD ── */
.chart-card {
    background:#fff; border-radius:14px; padding:14px;
    border:1px solid #e9eef5; box-shadow:0 2px 6px rgba(0,0,0,0.04);
    margin-bottom:12px;
}

/* ── FOLLOW-UP ALERT ── */
.followup-due {
    background:#fff7ed; border:1.5px solid #fed7aa;
    border-radius:10px; padding:10px 14px; margin-bottom:8px;
    font-size:13px; color:#92400e;
}

/* ── LOGIN ── */
.login-wrapper { max-width:360px; margin:80px auto 0 auto; }
.login-card {
    background:#fff; border-radius:20px; padding:36px 28px;
    box-shadow:0 8px 30px rgba(0,0,0,0.09); border:1px solid #e9eef5;
}
.login-logo { text-align:center; margin-bottom:24px; }
.login-logo-icon { font-size:40px; margin-bottom:8px; }
.login-logo-title { font-size:20px; font-weight:800; color:#1a1f2e; }
.login-logo-sub { font-size:12px; color:#64748b; margin-top:4px; }

/* ── MOBILE ── */
@media (max-width:600px) {
    .metric-value { font-size:22px; }
    .metric-label { font-size:10px; }
    .block-container { padding:0 8px 110px 8px !important; }
}
div[data-baseweb="select"] > div {
    background:#f8fafc !important; border:1.5px solid #e2e8f0 !important;
    border-radius:10px !important;
}
div[data-testid="column"] { padding-top:0 !important; }
div[data-testid="stBottom"] { display:none !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================
#  QR / BARCODE SCANNER  (jsQR + BarcodeDetector API)
# ============================================================
QR_SCANNER_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { box-sizing:border-box; margin:0; padding:0; }
body { background:#1a1f2e; font-family:sans-serif; }
#wrap { display:flex; flex-direction:column; align-items:center; padding:14px; gap:10px; }
#cam-box {
  position:relative; width:100%; max-width:340px;
  border-radius:14px; overflow:hidden; border:2px solid #2563eb; background:#000;
}
video { width:100%; display:block; }
canvas { display:none; }
#scan-line {
  position:absolute; left:8%; right:8%; height:2px;
  background:rgba(37,99,235,0.9); box-shadow:0 0 8px #2563eb;
  animation:scan 2s linear infinite;
}
@keyframes scan { 0%{top:8%} 50%{top:88%} 100%{top:8%} }
.corner { position:absolute; width:22px; height:22px; border-color:#2563eb; border-style:solid; }
#c-tl { top:8px;  left:8px;  border-width:3px 0 0 3px; border-radius:4px 0 0 0; }
#c-tr { top:8px;  right:8px; border-width:3px 3px 0 0; border-radius:0 4px 0 0; }
#c-bl { bottom:8px; left:8px; border-width:0 0 3px 3px; border-radius:0 0 0 4px; }
#c-br { bottom:8px; right:8px; border-width:0 3px 3px 0; border-radius:0 0 4px 0; }
#status { font-size:13px; color:#94a3b8; text-align:center; padding:0 8px; }
#result-box {
  display:none; background:#dcfce7; border:1.5px solid #16a34a;
  border-radius:10px; padding:12px 16px; width:100%; max-width:340px; text-align:center;
}
.rlbl { font-size:11px; color:#15803d; font-weight:700; text-transform:uppercase; }
.rval { font-size:18px; font-weight:800; color:#14532d; margin-top:4px; word-break:break-all; }
#btn-use {
  display:none; background:#2563eb; color:#fff; border:none;
  border-radius:10px; padding:12px; font-size:15px; font-weight:700;
  cursor:pointer; width:100%; max-width:340px;
}
#btn-use:hover { background:#1d4ed8; }
#btn-rescan {
  display:none; background:transparent; color:#64748b;
  border:1.5px solid #e2e8f0; border-radius:10px; padding:10px;
  font-size:14px; font-weight:600; cursor:pointer; width:100%; max-width:340px;
}
#err { font-size:12px; color:#f87171; text-align:center; padding:0 8px; display:none; }
</style>
</head>
<body>
<div id="wrap">
  <div id="cam-box">
    <video id="video" autoplay playsinline muted></video>
    <canvas id="canvas"></canvas>
    <div id="scan-line"></div>
    <div class="corner" id="c-tl"></div><div class="corner" id="c-tr"></div>
    <div class="corner" id="c-bl"></div><div class="corner" id="c-br"></div>
  </div>
  <div id="status">📷 Point camera at barcode or QR on the battery</div>
  <div id="err"></div>
  <div id="result-box">
    <div class="rlbl">Scanned Serial No.</div>
    <div class="rval" id="rval"></div>
  </div>
  <button id="btn-use" onclick="useResult()">✅ Use This Serial No.</button>
  <button id="btn-rescan" onclick="rescan()">🔄 Scan Again</button>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jsQR/1.4.0/jsQR.min.js"></script>
<script>
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const status = document.getElementById('status');
const errEl = document.getElementById('err');
const resBox = document.getElementById('result-box');
const rval = document.getElementById('rval');
const btnUse = document.getElementById('btn-use');
const btnRescan = document.getElementById('btn-rescan');
let scanning = true;
let scannedCode = '';

function startCamera() {
  navigator.mediaDevices.getUserMedia({
    video: { facingMode:{ideal:'environment'}, width:{ideal:1280}, height:{ideal:720} }
  }).then(stream => {
    video.srcObject = stream;
    video.play();
    requestAnimationFrame(tick);
  }).catch(() => {
    errEl.style.display = 'block';
    errEl.textContent = 'Camera permission denied. Please allow camera access.';
    status.style.display = 'none';
  });
}

function tick() {
  if (!scanning) return;
  if (video.readyState === video.HAVE_ENOUGH_DATA) {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const qr = jsQR(imgData.data, imgData.width, imgData.height, {inversionAttempts:'dontInvert'});
    if (qr && qr.data) { foundCode(qr.data.trim()); return; }
    if (window.BarcodeDetector) {
      if (!window._bd) window._bd = new BarcodeDetector({formats:['code_128','code_39','ean_13','ean_8','upc_a','upc_e','itf','codabar','qr_code','data_matrix','pdf417']});
      window._bd.detect(canvas).then(bs => { if(bs.length > 0 && scanning) foundCode(bs[0].rawValue.trim()); }).catch(()=>{});
    }
  }
  requestAnimationFrame(tick);
}

function foundCode(val) {
  if (!val) return;
  scanning = false;
  scannedCode = val;
  if (navigator.vibrate) navigator.vibrate([100,50,100]);
  status.textContent = '✅ Detected!';
  rval.textContent = val;
  resBox.style.display = 'block';
  btnUse.style.display = 'block';
  btnRescan.style.display = 'block';
  if (video.srcObject) video.srcObject.getTracks().forEach(t => t.stop());
}

function useResult() {
  window.parent.postMessage({type:'GBS_SCAN_RESULT', serial: scannedCode}, '*');
}

function rescan() {
  scanning = true; scannedCode = '';
  resBox.style.display='none'; btnUse.style.display='none'; btnRescan.style.display='none';
  status.textContent = '📷 Point camera at barcode or QR on the battery';
  startCamera();
}

startCamera();
</script>
</body>
</html>
"""

# JS bridge: listen for postMessage from scanner and redirect with ?scanned=
SCAN_BRIDGE_JS = """
<script>
(function(){
  if(window._gbsBridgeActive) return;
  window._gbsBridgeActive = true;
  window.addEventListener('message', function(e){
    if(e.data && e.data.type === 'GBS_SCAN_RESULT'){
      var serial = e.data.serial;
      var url = new URL(window.location.href);
      url.searchParams.set('scanned', serial);
      window.location.href = url.toString();
    }
  });
})();
</script>
"""


# ============================================================
#  HELPERS
# ============================================================
def fmt_inr(amount):
    try: return f"₹ {int(amount):,}"
    except: return "₹ 0"

def days_ago(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        delta = (date.today() - d).days
        if delta == 0: return "Today"
        if delta == 1: return "Yesterday"
        return f"{delta}d ago"
    except: return date_str

def followup_status(c):
    fu = c.get("follow_up_date")
    if not fu: return None, False
    try:
        fu_date = datetime.strptime(fu, "%Y-%m-%d").date()
        return fu_date.strftime("%d %b %Y"), fu_date < date.today()
    except: return None, False

def make_chart(labels, values, title, color="#2563eb"):
    fig, ax = plt.subplots(figsize=(5, 2.8))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")
    ax.bar(labels, values, color=color, width=0.55, zorder=3)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"₹{int(x/1000)}k" if x >= 1000 else f"₹{int(x)}"
    ))
    for sp in ["top","right"]: ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color("#e2e8f0")
    ax.spines["bottom"].set_color("#e2e8f0")
    ax.tick_params(colors="#64748b", labelsize=8)
    ax.set_title(title, fontsize=11, fontweight="bold", color="#1a1f2e", pad=8)
    ax.grid(axis="y", color="#e2e8f0", linewidth=0.8, zorder=0)
    plt.xticks(rotation=30, ha="right", fontsize=8)
    plt.tight_layout(pad=1.2)
    return fig

def validate_add_form(name, mobile, price):
    if not name.strip():                              return "Customer name is required."
    if not mobile.strip().isdigit() or len(mobile.strip()) < 10:
                                                      return "Enter a valid 10-digit mobile number."
    if price <= 0:                                    return "Battery price must be greater than ₹0."
    return ""


# ============================================================
#  LOGIN SCREEN
# ============================================================
if not st.session_state.logged_in:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="login-card">
      <div class="login-logo">
        <div class="login-logo-icon">🔋</div>
        <div class="login-logo-title">Gajanand Battery</div>
        <div class="login-logo-sub">{BRANCH_NAME}</div>
      </div>
    </div>""", unsafe_allow_html=True)

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
    st.markdown('<div style="text-align:center;font-size:11px;color:#94a3b8;padding:10px 0 4px 0;">Add to Home Screen for PWA experience 📱</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ============================================================
#  HEADER
# ============================================================
st.markdown(f"""
<div class="gbs-header">
  <div class="gbs-header-title">🔋 Gujarat Battery Service</div>
  <div class="gbs-header-badge">Gandhinagar</div>
</div>
<div class="header-spacer"></div>
""", unsafe_allow_html=True)

# Always inject scan bridge so it's active on every page
st.markdown(SCAN_BRIDGE_JS, unsafe_allow_html=True)


# ============================================================
#  BOTTOM NAV
# ============================================================
nav_labels = ["📊 Home", "➕ Add", "🔍 Search", "⏳ Due", "⚙️ More"]
nav_keys   = ["Dashboard", "Add Customer", "Search Customer", "Pending Payments", "More"]

nav_cols = st.columns(5)
for i, col in enumerate(nav_cols):
    with col:
        if st.button(nav_labels[i], key=f"nav_{i}", use_container_width=True):
            st.session_state.menu = nav_keys[i]
            st.session_state.scan_mode = None
            st.rerun()

st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)


# ============================================================
#  DASHBOARD
# ============================================================
if st.session_state.menu == "Dashboard":

    customers = get_all_customers()
    pending   = get_pending_customers()

    total_customers   = len(customers)
    pending_count     = len(pending)
    total_revenue     = sum(c.get("total_amount", 0) for c in customers)
    total_outstanding = sum(c.get("remaining_amount", 0) for c in pending)
    car_count  = sum(1 for c in customers if c.get("battery_type","") == "🚗Car")
    bike_count = sum(1 for c in customers if c.get("battery_type","") == "🏍️Bike")

    st.markdown(f"""
    <div class="brand-header">
      <div class="brand-name">Gujarat Battery Service</div>
      <div class="brand-branch">📍 {BRANCH_ADDRESS} &nbsp;•&nbsp; 📞 {BRANCH_PHONE}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-card"><div class="metric-label">Customers</div><div class="metric-value c-blue">{total_customers}</div></div>
      <div class="metric-card"><div class="metric-label">Revenue</div><div class="metric-value c-green" style="font-size:17px;">₹{total_revenue:,}</div></div>
      <div class="metric-card"><div class="metric-label">Pending</div><div class="metric-value c-red">{pending_count}</div></div>
    </div>
    <div class="metric-grid-2">
      <div class="metric-card"><div class="metric-label">🚗 Car</div><div class="metric-value c-blue">{car_count}</div></div>
      <div class="metric-card"><div class="metric-label">🏍️ Bike</div><div class="metric-value c-green">{bike_count}</div></div>
    </div>""", unsafe_allow_html=True)

    if total_outstanding > 0:
        st.markdown(f"""
        <div class="gbs-card" style="border-left:4px solid #dc2626;">
          <div style="font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">Total Outstanding</div>
          <div style="font-size:28px;font-weight:800;color:#dc2626;">₹ {total_outstanding:,}</div>
          <div style="font-size:12px;color:#94a3b8;margin-top:2px;">Across {pending_count} customers</div>
        </div>""", unsafe_allow_html=True)

    # Follow-ups due
    today = date.today()
    followups_today = []
    for c in customers:
        fu = c.get("follow_up_date")
        if not fu: continue
        try:
            if datetime.strptime(fu, "%Y-%m-%d").date() <= today:
                followups_today.append(c)
        except: pass

    if followups_today:
        st.markdown('<div class="section-label">🔔 Follow-ups Due</div>', unsafe_allow_html=True)
        for c in followups_today:
            fu_label, is_overdue = followup_status(c)
            if fu_label:
                st.markdown(f"""
                <div class="followup-due">
                  <strong>{c.get('name','')}</strong> &nbsp;
                  <span style="opacity:0.7;">📞 {c.get('mobile','')}</span><br>
                  📅 {fu_label} {'<span class="badge badge-red">Overdue</span>' if is_overdue else '<span class="badge badge-amber">Due Today</span>'}
                  {f"<br><span style='font-size:12px;'>{c.get('follow_up_note','')}</span>" if c.get('follow_up_note') else ''}
                </div>""", unsafe_allow_html=True)

    # Charts
    monthly_data = defaultdict(int)
    yearly_data  = defaultdict(int)
    for c in customers:
        ds = c.get("date","")
        if not ds: continue
        try:
            d = datetime.strptime(ds, "%Y-%m-%d")
            amt = int(c.get("total_amount", 0))
            monthly_data[d.strftime("%b %Y")] += amt
            yearly_data[d.strftime("%Y")]     += amt
        except: pass

    st.markdown('<div class="section-label">📈 Sales Analytics</div>', unsafe_allow_html=True)
    ch1, ch2 = st.columns(2)
    with ch1:
        if monthly_data:
            months = sorted(monthly_data.keys(), key=lambda x: datetime.strptime(x, "%b %Y"))
            fig = make_chart(months, [monthly_data[m] for m in months], "Monthly Sales", "#2563eb")
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.pyplot(fig, use_container_width=True); plt.close(fig)
            st.markdown('</div>', unsafe_allow_html=True)
    with ch2:
        if yearly_data:
            years = sorted(yearly_data.keys())
            fig = make_chart(years, [yearly_data[y] for y in years], "Yearly Sales", "#16a34a")
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.pyplot(fig, use_container_width=True); plt.close(fig)
            st.markdown('</div>', unsafe_allow_html=True)

    # Recent customers
    st.markdown('<div class="section-label">👥 Recent Customers</div>', unsafe_allow_html=True)
    for c in sorted(customers, key=lambda x: x.get("date",""), reverse=True)[:5]:
        rem = c.get("remaining_amount", 0)
        st.markdown(f"""
        <div class="gbs-card" style="padding:13px 15px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <div style="font-size:15px;font-weight:700;">{c.get('name','')}</div>
              <div style="font-size:12px;color:#64748b;">📞 {c.get('mobile','')} • {c.get('battery_type','')}</div>
            </div>
            <div style="text-align:right;">
              <div style="font-size:14px;font-weight:700;color:#16a34a;">{fmt_inr(c.get('total_amount',0))}</div>
              <div style="font-size:11px;color:#94a3b8;">{days_ago(c.get('date',''))}</div>
            </div>
          </div>
          {f'<div style="margin-top:6px;"><span class="badge badge-red">Due: {fmt_inr(rem)}</span></div>' if rem > 0 else ''}
        </div>""", unsafe_allow_html=True)


# ============================================================
#  ADD CUSTOMER
# ============================================================
elif st.session_state.menu == "Add Customer":

    st.markdown('<div class="page-title">➕ New Customer</div>', unsafe_allow_html=True)

    # ── SCANNER PANEL ──
    if st.session_state.scan_mode == "add":
        st.markdown('<div class="gbs-card" style="padding:0;overflow:hidden;border-radius:16px;">', unsafe_allow_html=True)
        components.html(QR_SCANNER_HTML, height=450, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.scanned_serial:
            st.success(f"✅ Scanned Serial: **{st.session_state.scanned_serial}**  — Close scanner to use it in the form.")

        if st.button("❌ Close Scanner & Fill Form", use_container_width=True):
            st.session_state.scan_mode = None
            st.rerun()
        st.stop()

    # ── FORM ──
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
        scanned_val  = st.session_state.scanned_serial
        serial_no    = st.text_input(
            "Serial No",
            value=scanned_val if scanned_val else "",
            placeholder="Type or scan barcode / QR"
        )
    with c2:
        brand      = st.text_input("Brand", placeholder="e.g. Amaron, Exide")
        vehicle_no = st.text_input("Vehicle No", placeholder="GJ-XX-XXXX")

    st.markdown('<div class="scan-btn">', unsafe_allow_html=True)
    if st.button("📷  Scan Battery Barcode / QR  →  Auto-fill Serial No", use_container_width=True):
        st.session_state.scan_mode = "add"
        st.session_state.scanned_serial = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Pricing</div>', unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    with p1:
        price    = st.number_input("Battery Price (₹) *", min_value=0, step=100)
    with p2:
        discount = st.number_input("Discount (₹)", min_value=0, step=50)

    total_display = price - discount
    if price > 0:
        st.markdown(f"""
        <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;padding:10px 14px;margin:4px 0 10px 0;">
          <span style="font-size:13px;color:#0369a1;font-weight:700;">Total: ₹ {total_display:,}</span>
          {f'<span style="font-size:12px;color:#16a34a;margin-left:12px;">Discount: ₹ {discount:,}</span>' if discount > 0 else ''}
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Date & Notes</div>', unsafe_allow_html=True)
    purchase_date = st.date_input("Purchase Date", value=date.today())
    note = st.text_area("Note", height=70, placeholder="Warranty, condition, old battery details...")

    st.markdown('<div class="section-label">Payment</div>', unsafe_allow_html=True)
    has_remaining    = st.checkbox("Has Remaining Amount")
    remaining_amount = 0
    payment_note     = ""
    if has_remaining:
        remaining_amount = st.number_input("Remaining Amount (₹)", min_value=0, step=100)
        payment_note     = st.text_area("Payment Note", height=60, placeholder="Promised date, installment plan...")

    st.markdown('<div class="section-label">📅 Follow-up (Optional)</div>', unsafe_allow_html=True)
    set_followup       = st.checkbox("Schedule a Follow-up")
    follow_up_date_val = None
    follow_up_note_val = ""
    if set_followup:
        fu_c1, fu_c2 = st.columns(2)
        with fu_c1:
            fu_date = st.date_input("Follow-up Date", value=date.today() + timedelta(days=30))
            follow_up_date_val = fu_date.strftime("%Y-%m-%d")
        with fu_c2:
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
            if set_followup and follow_up_date_val:
                all_c  = get_all_customers()
                latest = sorted(all_c, key=lambda x: x.get("created_at", datetime.min), reverse=True)
                if latest:
                    update_customer(latest[0]["id"], {
                        "follow_up_date": follow_up_date_val,
                        "follow_up_note": follow_up_note_val
                    })
            st.session_state.scanned_serial = ""
            st.success("✅ Customer saved successfully!")
            time.sleep(0.4)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
#  SEARCH CUSTOMER  — overlap FIXED, QR scan added
# ============================================================
elif st.session_state.menu == "Search Customer":

    st.markdown('<div class="page-title">🔍 Search Customer</div>', unsafe_allow_html=True)

    # ── SCANNER PANEL ──
    if st.session_state.scan_mode == "search":
        st.markdown('<div class="gbs-card" style="padding:0;overflow:hidden;border-radius:16px;">', unsafe_allow_html=True)
        components.html(QR_SCANNER_HTML, height=450, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.scanned_serial:
            st.success(f"✅ Scanned: **{st.session_state.scanned_serial}** — Close to search.")

        if st.button("❌ Close Scanner & Search", use_container_width=True):
            st.session_state.scan_mode = None
            st.rerun()
        st.stop()

    # ── SEARCH BAR + SCAN BUTTON ──
    s1, s2 = st.columns([4, 1])
    with s1:
        default_q = st.session_state.scanned_serial if st.session_state.scanned_serial else ""
        query = st.text_input(
            "", value=default_q,
            placeholder="Name, mobile, serial no, vehicle no...",
            label_visibility="collapsed"
        )
    with s2:
        st.markdown('<div class="scan-btn">', unsafe_allow_html=True)
        if st.button("📷 Scan", use_container_width=True):
            st.session_state.scan_mode = "search"
            st.session_state.scanned_serial = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

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
            st.markdown(f'<div style="font-size:13px;color:#64748b;margin-bottom:10px;">{len(results)} result(s)</div>', unsafe_allow_html=True)

        for c in results:
            remaining = c.get("remaining_amount", 0)
            fu_label, fu_overdue = followup_status(c)
            card_id    = c["id"]
            expand_key = f"expand_{card_id}"
            if expand_key not in st.session_state:
                st.session_state[expand_key] = False

            dot          = "🔴" if remaining > 0 else "🟢"
            status_badge = (
                f'<span class="badge badge-red">Due {fmt_inr(remaining)}</span>'
                if remaining > 0
                else '<span class="badge badge-green">Paid</span>'
            )

            # ── CARD HEADER — no expander, no overlap ──
            st.markdown(f"""
            <div class="cust-card">
              <div class="cust-card-header">
                <div style="min-width:0; flex:1;">
                  <div class="cust-card-name">{dot}&nbsp;{c.get('name','')}</div>
                  <div class="cust-card-sub">📞 {c.get('mobile','')} &nbsp;•&nbsp; {c.get('battery_type','—')}</div>
                  <div class="cust-card-sub">📅 {c.get('date','—')} &nbsp;•&nbsp; Serial: {c.get('serial_no','—')}</div>
                </div>
                <div class="cust-card-right">
                  {status_badge}
                  <div style="font-size:12px;color:#94a3b8;margin-top:4px;">{fmt_inr(c.get('total_amount',0))}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Toggle button
            tog = "▲ Close" if st.session_state[expand_key] else "▼ Details & Edit"
            if st.button(tog, key=f"tog_{card_id}", use_container_width=True):
                st.session_state[expand_key] = not st.session_state[expand_key]
                st.rerun()

            # ── EXPANDED DETAILS + EDIT ──
            if st.session_state[expand_key]:
                st.markdown('<div class="gbs-card" style="margin-top:-2px;">', unsafe_allow_html=True)

                d1, d2 = st.columns(2)
                with d1:
                    st.markdown(f"**🔋 Battery:** {c.get('battery_name','—')} ({c.get('brand','—')})")
                    st.markdown(f"**🔢 Serial:** {c.get('serial_no','—')}")
                    st.markdown(f"**🚘 Vehicle:** {c.get('vehicle_no','—')}")
                with d2:
                    st.markdown(f"**💰 Total:** {fmt_inr(c.get('total_amount',0))}")
                    st.markdown(f"**📅 Date:** {c.get('date','—')}")
                    if remaining > 0:
                        st.markdown(f"**⚠️ Due:** {fmt_inr(remaining)}")
                if c.get("note"):
                    st.markdown(f"**📝 Note:** {c.get('note')}")
                if fu_label:
                    st.markdown(f"**📅 Follow-up:** {fu_label} {'🔴 Overdue' if fu_overdue else '🟡 Scheduled'}")

                st.markdown('<div class="gbs-divider"></div>', unsafe_allow_html=True)
                st.markdown('<div style="font-size:13px;font-weight:700;color:#374151;margin-bottom:8px;">✏️ Edit</div>', unsafe_allow_html=True)

                e1, e2 = st.columns(2)
                with e1:
                    e_name    = st.text_input("Name",       c.get("name",""),         key=f"en_{card_id}")
                    e_mobile  = st.text_input("Mobile",     c.get("mobile",""),       key=f"em_{card_id}")
                    e_battery = st.text_input("Battery",    c.get("battery_name",""), key=f"eb_{card_id}")
                    e_brand   = st.text_input("Brand",      c.get("brand",""),        key=f"ebr_{card_id}")
                with e2:
                    e_serial  = st.text_input("Serial No",  c.get("serial_no",""),   key=f"es_{card_id}")
                    e_vehicle = st.text_input("Vehicle No", c.get("vehicle_no",""),  key=f"ev_{card_id}")
                    e_price   = st.number_input("Price",    int(c.get("price",0)),    key=f"ep_{card_id}")
                    e_disc    = st.number_input("Discount", int(c.get("discount",0)), key=f"ed_{card_id}")

                e_remaining = st.number_input("Remaining (₹)", int(c.get("remaining_amount",0)), key=f"er_{card_id}")
                e_note      = st.text_area("Note", c.get("note",""), height=70, key=f"enote_{card_id}")
                e_fu_date   = st.text_input("Follow-up Date (YYYY-MM-DD)", c.get("follow_up_date","") or "", key=f"efu_{card_id}")
                e_fu_note   = st.text_input("Follow-up Reason", c.get("follow_up_note",""), key=f"efun_{card_id}")

                e_total = e_price - e_disc
                st.markdown(f'<div style="font-size:13px;color:#2563eb;font-weight:700;margin:4px 0 10px 0;">Total: ₹ {e_total:,}</div>', unsafe_allow_html=True)

                eb1, eb2 = st.columns(2)
                with eb1:
                    if st.button("✏️ Update", key=f"upd_{card_id}", use_container_width=True):
                        update_customer(card_id, {
                            "name": e_name.strip(), "mobile": e_mobile.strip(),
                            "battery_name": e_battery.strip(), "brand": e_brand.strip(),
                            "serial_no": e_serial.strip(), "vehicle_no": e_vehicle.strip(),
                            "price": e_price, "discount": e_disc, "total_amount": e_total,
                            "remaining_amount": e_remaining, "has_remaining": e_remaining > 0,
                            "note": e_note.strip(),
                            "follow_up_date": e_fu_date.strip() or None,
                            "follow_up_note": e_fu_note.strip(),
                        })
                        st.success("✅ Updated")
                        st.rerun()
                with eb2:
                    if st.button("🗑️ Delete", key=f"del_{card_id}", use_container_width=True):
                        delete_customer(card_id)
                        st.error("Deleted")
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

    elif query and len(query.strip()) < 2:
        st.markdown('<div style="color:#94a3b8;font-size:13px;">Type at least 2 characters...</div>', unsafe_allow_html=True)


# ============================================================
#  PENDING PAYMENTS
# ============================================================
elif st.session_state.menu == "Pending Payments":

    pending   = get_pending_customers()
    total_due = sum(c.get("remaining_amount", 0) for c in pending)

    st.markdown('<div class="page-title">⏳ Pending Payments</div>', unsafe_allow_html=True)

    if not pending:
        st.success("🎉 All payments cleared! No pending dues.")
    else:
        st.markdown(f"""
        <div class="gbs-card" style="border-left:4px solid #dc2626;margin-bottom:14px;">
          <div style="font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;">Total Outstanding</div>
          <div style="font-size:26px;font-weight:800;color:#dc2626;">₹ {total_due:,}</div>
          <div style="font-size:12px;color:#94a3b8;">{len(pending)} customers</div>
        </div>""", unsafe_allow_html=True)

        for c in sorted(pending, key=lambda x: x.get("remaining_amount",0), reverse=True):
            rem   = c.get("remaining_amount", 0)
            total = c.get("total_amount", 0)
            paid  = total - rem
            pct   = int((paid / total * 100)) if total > 0 else 0
            fu_label, fu_overdue = followup_status(c)

            st.markdown(f"""
            <div class="gbs-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                  <div style="font-size:17px;font-weight:700;">{c.get('name','')}</div>
                  <div style="font-size:12px;color:#64748b;">📞 {c.get('mobile','')} &nbsp;•&nbsp; {c.get('battery_type','')}</div>
                  <div style="font-size:12px;color:#64748b;">📅 {c.get('date','—')} &nbsp;•&nbsp; {c.get('battery_name','—')}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:15px;font-weight:800;color:#dc2626;">₹ {rem:,} due</div>
                  <div style="font-size:11px;color:#94a3b8;">of ₹ {total:,}</div>
                </div>
              </div>
              <div style="background:#f1f5f9;border-radius:6px;height:6px;margin:10px 0 4px 0;overflow:hidden;">
                <div style="background:#16a34a;width:{pct}%;height:100%;border-radius:6px;"></div>
              </div>
              <div style="font-size:11px;color:#94a3b8;margin-bottom:8px;">Paid {pct}% &nbsp;(₹ {paid:,})</div>
              {f'<div style="font-size:12px;color:#92400e;margin-bottom:4px;">📅 Follow-up: {fu_label} {"🔴" if fu_overdue else "🟡"}</div>' if fu_label else ''}
              {f'<div style="font-size:12px;color:#64748b;margin-bottom:6px;">💬 {c.get("payment_note","")}</div>' if c.get("payment_note") else ''}
            </div>""", unsafe_allow_html=True)

            payment = st.number_input(
                f"Add payment — {c.get('name','')}",
                min_value=0, max_value=int(rem), step=100, key=f"pay_{c['id']}"
            )
            pb1, pb2 = st.columns(2)
            with pb1:
                if st.button("➕ Add Payment", key=f"addpay_{c['id']}", use_container_width=True):
                    if payment <= 0:
                        st.warning("Enter an amount.")
                    else:
                        new_rem = rem - payment
                        update_customer(c["id"], {"remaining_amount": new_rem, "has_remaining": new_rem > 0})
                        st.success(f"✅ Added ₹{payment:,}. Remaining: ₹{new_rem:,}")
                        st.rerun()
            with pb2:
                if st.button("✔ Mark Paid", key=f"markpaid_{c['id']}", use_container_width=True):
                    update_customer(c["id"], {"remaining_amount": 0, "has_remaining": False})
                    st.success("✅ Cleared")
                    st.rerun()
            st.markdown('<div class="gbs-divider"></div>', unsafe_allow_html=True)


# ============================================================
#  MORE
# ============================================================
elif st.session_state.menu == "More":

    st.markdown('<div class="page-title">⚙️ More</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="gbs-card">
      <div style="font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;margin-bottom:8px;">Branch Info</div>
      <div style="font-size:15px;font-weight:800;">🔋 Gajanand Battery</div>
      <div style="font-size:13px;color:#64748b;margin-top:4px;">📍 {BRANCH_ADDRESS}</div>
      <div style="font-size:13px;color:#64748b;margin-top:2px;">📞 {BRANCH_PHONE}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">📥 Export Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="gbs-card">', unsafe_allow_html=True)
    if st.button("📥 Export All Customers (CSV)", use_container_width=True):
        customers = get_all_customers()
        if customers:
            df = pd.DataFrame(customers)
            for col in ["id","created_at","follow_up_date","follow_up_note"]:
                if col in df.columns: df = df.drop(columns=[col])
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download", data=csv, file_name=f"gbs_customers_{date.today()}.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("No data.")
    if st.button("📥 Export Pending Payments (CSV)", use_container_width=True):
        pending = get_pending_customers()
        if pending:
            df = pd.DataFrame(pending)
            for col in ["id","created_at"]:
                if col in df.columns: df = df.drop(columns=[col])
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Pending", data=csv, file_name=f"gbs_pending_{date.today()}.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("No pending data.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">📊 Top Brands</div>', unsafe_allow_html=True)
    customers = get_all_customers()
    if customers:
        brands = defaultdict(int)
        for c in customers:
            b = c.get("brand","").strip()
            if b: brands[b] += 1
        top_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5]
        st.markdown('<div class="gbs-card">', unsafe_allow_html=True)
        for brand_name, cnt in top_brands:
            pct = int(cnt / len(customers) * 100)
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px;">
              <span>{brand_name}</span><span style="color:#2563eb;font-weight:700;">{cnt} ({pct}%)</span>
            </div>
            <div style="background:#f1f5f9;border-radius:4px;height:4px;margin-bottom:10px;">
              <div style="background:#2563eb;width:{pct}%;height:100%;border-radius:4px;"></div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="gbs-card" style="border:1px dashed #cbd5e1;">
      <div style="font-size:13px;font-weight:700;margin-bottom:6px;">📱 Install as App</div>
      <div style="font-size:12px;color:#64748b;">
        <b>Android:</b> Chrome → ⋮ → Add to Home Screen<br>
        <b>iOS:</b> Safari → Share → Add to Home Screen<br><br>
        Opens fullscreen like a native app 🚀
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="gbs-card">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:13px;color:#64748b;margin-bottom:10px;">Logged in as <strong>{APP_USERNAME}</strong></div>', unsafe_allow_html=True)
    if st.button("🔓 Logout", use_container_width=True):
        st.session_state.logged_in = False
        clear_persistent_login()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
