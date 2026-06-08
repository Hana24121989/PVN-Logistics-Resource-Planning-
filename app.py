
import streamlit as st
import math
from datetime import date

st.title("📦 Simple Resource Planning")

# -----------------------------
# INPUT
# -----------------------------
st.header("Input")

st.header("Process")

process = st.selectbox(
    "Select Operation",
    ["Inbound PIT", "Inbound Interco", "VAS"]
)

mode = st.selectbox(
    "Select Mode",
    ["Outsource", "Overtime"]
)


if process == "Inbound PIT":
    productivity_day = 130
    productivity_hour = 17.3
    uom = "Carton"

elif process == "Inbound Interco":
    productivity_day = 810
    productivity_hour = 108.0
    uom = "Pcs"

elif process == "VAS":
    productivity_day = 2000
    productivity_hour = 266.7
    uom = "Pcs"




backlog = st.number_input(f"Backlog ({uom})", value=5000)
current_hc = st.number_input("Current Headcount", value=2)

start_date = st.date_input("Start Date", date(2026, 5, 23))
end_date = st.date_input("End Date", date(2026, 5, 26))

# -----------------------------
# FIXED RULE (ẩn đi cho bạn)
# -----------------------------


day1 = 0.55
day2 = 0.9
day3 = 0.9
day4 = 1

# -----------------------------
# CALCULATION
daily_rate = 637942

ot_operator_rate = 97905
ot_admin_rate = 141240
ot_reachtruck_rate = 104325

# -----------------------------


net_days = (end_date - start_date).days  

if net_days <= 0:
    st.warning("Ngày không hợp lệ")  

else:
    # -------- TRAINING --------
    if net_days == 1:
        effective_days = 0.55
    elif net_days == 2:
        effective_days = 0.55 + 0.9
    elif net_days == 3:
        effective_days = 0.55 + 0.9 + 0.9
    else:
        effective_days = 0.55 + 0.9 + 0.9 + (net_days - 3)

    # -------- DAY CAPACITY --------
    capacity_current = current_hc * productivity_day * net_days
    remaining = backlog - capacity_current
    remaining = max(0, remaining)

    # -------- OUTSOURCE --------
    capacity_per_hc = productivity_day * effective_days

    if remaining <= 0:
        hc_outsource = 0
    else:
        hc_outsource = math.ceil(remaining / capacity_per_hc)

    additional_cost = hc_outsource * daily_rate * net_days

    # -------- OVERTIME --------
    ot_working_hours = 3.5
    ot_paid_hours = 4

    capacity_ot_per_hc = productivity_hour * ot_working_hours * net_days

    if remaining <= 0:
        hc_ot_total = 0
    else:
        hc_ot_total = math.ceil(remaining / capacity_ot_per_hc)

    ot_operator_cost = hc_ot_total * ot_operator_rate * ot_paid_hours * net_days
    ot_admin_cost = 1 * ot_admin_rate * ot_paid_hours * net_days
    ot_reach_cost = 1 * ot_reachtruck_rate * ot_paid_hours * net_days

    total_ot_cost = ot_operator_cost + ot_admin_cost + ot_reach_cost

    # -------- OUTPUT --------
    
st.header("Result")

st.write(f"Net days: {net_days}")
st.write(f"Remaining workload: {int(remaining)} {uom}")

if mode == "Outsource":
    st.write(f"👉 HC needed (Outsource): **{hc_outsource}**")
    st.write(f"💰 Outsource Cost (VND): {additional_cost:,.0f}")

elif mode == "Overtime":
    st.write(f"👉 Total HC needed (OT): **{hc_ot_total}**")
    st.write(f"👉 Additional HC needed (OT): **{max(0, hc_ot_total - current_hc)}**")

    st.write("💰 OT Cost breakdown:")
    st.write(f"Operator: {ot_operator_cost:,.0f}")
    st.write(f"Admin: {ot_admin_cost:,.0f}")
    st.write(f"Reachtruck: {ot_reach_cost:,.0f}")


st.success(f"👉 Total OT Cost: {total_ot_cost:,.0f}")


st.header("Comparison")

col1, col2 = st.columns(2)

# --- OUTSOURCE ---
with col1:
    st.subheader("Outsource")
    st.write(f"HC: {hc_outsource}")
    st.write(f"Cost: {additional_cost:,.0f} VND")

# --- OVERTIME ---
with col2:
    st.subheader("Overtime")
    st.write(f"HC: {hc_ot_total}")
    st.write(f"Cost: {total_ot_cost:,.0f} VND")

# --- DECISION ---
st.header("Recommendation")

if additional_cost < total_ot_cost:
    st.success("✅ Recommend: Outsource (cheaper)")

elif total_ot_cost < additional_cost:
    st.success("✅ Recommend: Overtime (cheaper)")

else:
    st.info("⚖️ Both options have same cost")
