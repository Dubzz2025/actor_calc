import streamlit as st
import pandas as pd

# --- 1. CONFIG & STYLING ---
st.set_page_config(
    page_title="ATPA Cast Calc",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 1px solid #dcdcdc;
    }
    .big-number {
        font-size: 32px;
        font-weight: bold;
        color: #2e7d32;
    }
    .sub-label {
        font-size: 14px;
        color: #555;
    }
    .warning-box {
        background-color: #ffcccc;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ff0000;
        color: #990000;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎭 ATPA Actor Deal Calculator")

# --- 2. SIDEBAR - GLOBAL SETTINGS ---
with st.sidebar:
    st.header("Deal Parameters")
    
    agreement = st.selectbox("Agreement", ["ATPA (TV)", "AFFCA (Film)"], index=0)
    performer_class = st.radio("Performer Class", ["Class 1", "Class 2"], horizontal=True)
    
    st.divider()
    st.subheader("💰 Award Rate Settings")
    st.caption("Update these rates as per current MEAA sheets.")

    # 1. Determine Defaults
    if agreement == "ATPA (TV)":
        def_wk = 1250.00 if performer_class == "Class 1" else 1100.00
        def_d = 350.00 if performer_class == "Class 1" else 300.00
    else:
        def_wk = 1350.00 if performer_class == "Class 1" else 1200.00
        def_d = 400.00 if performer_class == "Class 1" else 350.00

    # 2. Allow User to Override Defaults
    current_min_weekly = st.number_input("Weekly Minimum ($)", value=def_wk, step=10.0)
    current_min_daily = st.number_input("Daily Minimum ($)", value=def_d, step=10.0)

    st.divider()
    
    st.subheader("Global Fringes")
    super_rate = st.number_input("Superannuation %", value=12.0, step=0.5) / 100

# --- 3. MAIN CALCULATOR (TABS) ---
tab_weekly, tab_daily = st.tabs(["🗓️ Weekly Deal", "☀️ Daily Deal"])

# ==========================================
#          WEEKLY CALCULATOR
# ==========================================
with tab_weekly:
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.subheader("1. Rights & Loadings")
        st.caption("Select these FIRST to determine the Divisor.")
        
        rights_config = {
            "Aus Free TV (x4) OR (x5) (25%)": 0.25,
            "World Free/Pay TV (ex US) (25%)": 0.25,
            "World Theatrical (25%)": 0.25,
            "World Ancillary (ex Aust) (20%)": 0.20,
            "Aus Ancillary & Pay TV (20%)": 0.20
        }
        
        active_rights_pct = 0.0
        for label, pct in rights_config.items():
            if st.checkbox(label, key=f"wk_{label}"):
                active_rights_pct += pct
        
        st.info(f"**Total Loadings:** {active_rights_pct*100:.0f}% (Multiplier: {1 + active_rights_pct:.2f}x)")

        st.subheader("2. Financials")
        
        # Calculation Mode Toggle
        calc_mode = st.radio(
            "Calculation Method:", 
            ["Build Up (Base + Margin)", "Reverse from Total (Gross to Net)", "Derive from Daily Ratio"],
            horizontal=True
        )

        weekly_hours = st.selectbox("Weekly Hours", [40, 50, 60], index=1)
        base_award_wk = st.number_input("Weekly Award Min ($)", value=current_min_weekly, step=10.0)
        
        bnf_weekly = 0.0
        personal_margin = 0.0
        composite_rate = 0.0

        # --- LOGIC BRANCHING ---
        if calc_mode == "Build Up (Base + Margin)":
            personal_margin = st.number_input("Personal Margin ($)", value=0.0, step=50.0)
            bnf_weekly = base_award_wk + personal_margin
            rights_amount = bnf_weekly * active_rights_pct
            composite_rate = bnf_weekly + rights_amount
        
        elif calc_mode == "Derive from Daily Ratio":
            # UPDATED FORMULA: Weekly BNF = Weekly Total x (Daily Min / Daily Total)
            
            # 1. Inputs to establish the Ratio
            col_a, col_b = st.columns(2)
            with col_a:
                daily_min_input = st.number_input("Daily Award Min ($)", value=current_min_daily, step=10.0)
            with col_b:
                total_daily_fee_input = st.number_input("Total Daily Fee ($)", value=1000.0, step=50.0)
            
            # 2. Input the Target Weekly
            target_weekly_total = st.number_input("Target Weekly Total ($)", value=4000.0, step=100.0)

            # 3. Calculate Ratio & Weekly BNF
            if total_daily_fee_input > 0:
                # This determines what % of the fee is "Base" (BNF)
                base_ratio = daily_min_input / total_daily_fee_input
                
                # Apply that % to the Weekly Total
                bnf_weekly = target_weekly_total * base_ratio
                
                st.caption(f"ℹ️ Base Ratio: {base_ratio*100:.2f}% (derived from Daily deal)")
            else:
                bnf_weekly = 0.0
                
            personal_margin = bnf_weekly - base_award_wk
            
            # Note: In this mode, we calculate Rights based on the derived BNF to check logic, 
            # but the Composite is driven by the Target Total.
            rights_amount = bnf_weekly * active_rights_pct
            composite_rate = target_weekly_total

        else:
            # REVERSE CALCULATION (Gross to Net)
            # This is the standard Gemini Method (Total / Multiplier)
            target_composite = st.number_input("Target Weekly Composite Fee ($)", value=2000.0, step=50.0)
            
            divisor = 1 + active_rights_pct
            bnf_weekly = target_composite / divisor
            personal_margin = bnf_weekly - base_award_wk
            
            rights_amount = bnf_weekly * active_rights_pct
            composite_rate = target_composite

        # Safety Check
        if bnf_weekly < base_award_wk:
             st.markdown(f'<div class="warning-box">⚠️ Illegal Rate! BNF (${bnf_weekly:,.2f}) is below Minimum (${base_award_wk})</div>', unsafe_allow_html=True)

        st.success(f"**Calculated BNF:** ${bnf_weekly:,.2f}")

        st.subheader("3. Overtime")
        ot_amount = st.number_input("Overtime / 6th Day ($)", value=0.0, step=100.0, key="wk_ot")

    # --- WEEKLY CALCULATIONS ---
    holiday_pay = (composite_rate / 40 * 50) / 12
    
    total_fee_pre_fringe = composite_rate + ot_amount
    super_amount = total_fee_pre_fringe * super_rate
    
    grand_total_weekly = total_fee_pre_fringe + holiday_pay + super_amount

    # --- WEEKLY OUTPUT ---
    with col2:
        st.markdown("### 🧾 Cost Breakdown")
        
        line_items = {
            "Weekly Award Min": base_award_wk,
            "Personal Margin": personal_margin,
            "➤ BNF": bnf_weekly,
            f"Rights Loadings ({active_rights_pct*100:.0f}%)": rights_amount,
            "➤ Composite Rate": composite_rate,
            "Overtime/6th Day": ot_amount,
            "➤ Total Fee (Gross)": total_fee_pre_fringe,
            "Holiday Pay": holiday_pay,
            f"Superannuation ({super_rate*100}%)": super_amount
        }
        
        for k, v in line_items.items():
            c_a, c_b = st.columns([3, 1])
            if "➤" in k:
                c_a.markdown(f"**{k}**")
                c_b.markdown(f"**${v:,.2f}**")
            else:
                c_a.write(k)
                c_b.write(f"${v:,.2f}")
        
        st.divider()
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="sub-label">Est. Total Cost to Production (Weekly)</div>
            <div class="big-number">${grand_total_weekly:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
#          DAILY CALCULATOR
# ==========================================
with tab_daily:
    d_col1, d_col2 = st.columns([1, 1.5])
    
    with d_col1:
        st.subheader("1. Rights & Loadings")
        active_rights_pct_daily = 0.0
        for label, pct in rights_config.items():
            if st.checkbox(label, key=f"day_{label}"):
                active_rights_pct_daily += pct
        
        st.info(f"**Total Loadings:** {active_rights_pct_daily*100:.0f}%")

        st.subheader("2. Financials")
        
        calc_mode_daily = st.radio(
            "Calculation Method:", 
            ["Build Up", "Reverse from Total"],
            horizontal=True,
            key="calc_mode_daily"
        )
        
        daily_hours = st.selectbox("Daily Hours", [8, 10], index=1)
        base_award_daily = st.number_input("Daily Award Minimum ($)", value=current_min_daily, step=10.0, key="d_award_base")

        bnf_daily = 0.0
        margin_daily = 0.0
        composite_daily = 0.0

        if calc_mode_daily == "Build Up":
            margin_daily = st.number_input("Personal Margin ($)", value=0.0, step=50.0, key="d_margin")
            bnf_daily = base_award_daily + margin_daily
            rights_amt_daily = bnf_daily * active_rights_pct_daily
            composite_daily = bnf_daily + rights_amt_daily
        else:
            # REVERSE
            target_daily = st.number_input("Target Daily Composite ($)", value=1000.0, step=50.0)
            divisor_d = 1 + active_rights_pct_daily
            bnf_daily = target_daily / divisor_d
            margin_daily = bnf_daily - base_award_daily
            
            if bnf_daily < base_award_daily:
                st.markdown(f'<div class="warning-box">⚠️ Illegal Rate! BNF (${bnf_daily:,.2f}) < Min (${base_award_daily})</div>', unsafe_allow_html=True)
            
            rights_amt_daily = bnf_daily * active_rights_pct_daily
            composite_daily = target_daily

        # Rehearsals - Stand Alone
        st.subheader("3. Extras")
        rehearsal_hours_input = st.number_input("Rehearsal Hours", min_value=0.0, step=0.5)
        rehearsal_cost = 0.0
        effective_reh_hours = 0.0
        
        if rehearsal_hours_input > 0:
            effective_reh_hours = max(rehearsal_hours_input, 2.5)
            if effective_reh_hours > rehearsal_hours_input:
                st.caption(f"ℹ️ Minimum 2.5h call applied (Input: {rehearsal_hours_input}h)")
            
            rehearsal_cost = (bnf_daily / 8) * effective_reh_hours

        st.subheader("4. Overtime")
        ot_hours_daily = st.number_input("OT Hours", value=0.0, step=0.5)
        
        # OT Calc
        hourly_rate = bnf_daily / 8
        est_ot_cost = 0.0
        if ot_hours_daily > 0:
            est_ot_cost = (hourly_rate * 1.5 * 2) + (hourly_rate * 2.0 * (ot_hours_daily - 2)) if ot_hours_daily > 2 else (hourly_rate * 1.5 * ot_hours_daily)
        
        ot_amt_daily = st.number_input("Overtime Amount ($)", value=est_ot_cost, step=50.0)

    # --- DAILY CALCULATIONS ---
    holiday_pay_daily = composite_daily / 12 
    total_superable = composite_daily + ot_amt_daily + rehearsal_cost
    super_daily = total_superable * super_rate
    grand_total_daily = total_superable + holiday_pay_daily + super_daily

    # --- DAILY OUTPUT ---
    with d_col2:
        st.markdown("### 🧾 Cost Breakdown (Daily)")
        
        line_items_d = {
            "Daily Award": base_award_daily,
            "Personal Margin": margin_daily,
            "➤ BNF": bnf_daily,
            f"Rights Loadings ({active_rights_pct_daily*100:.0f}%)": rights_amt_daily,
            "➤ Composite Rate": composite_daily,
            f"Overtime ({ot_hours_daily}hrs)": ot_amt_daily,
            f"Rehearsals ({effective_reh_hours}hrs @ Stand Alone)": rehearsal_cost,
            "➤ Total Fee (Gross)": total_superable,
            "Holiday Pay (1/12th of Comp)": holiday_pay_daily,
            f"Superannuation ({super_rate*100}%)": super_daily
        }
        
        for k, v in line_items_d.items():
            c_a, c_b = st.columns([3, 1])
            if "➤" in k:
                c_a.markdown(f"**{k}**")
                c_b.markdown(f"**${v:,.2f}**")
            else:
                c_a.write(k)
                c_b.write(f"${v:,.2f}")
                
        st.divider()
        st.markdown(f"""
        <div class="metric-card">
            <div class="sub-label">Est. Total Cost to Production (Daily)</div>
            <div class="big-number">${grand_total_daily:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

# --- 4. EXPORT / COPY ---
st.divider()
if st.button("📋 Copy Deal Points"):
    if tab_weekly:
        summary = f"""
        DEAL MEMO (ATPA - {performer_class})
        -------------------------
        Basis: {weekly_hours} Hour Week
        BNF: ${bnf_weekly:,.2f} (Base ${base_award_wk} + Margin ${personal_margin:,.2f})
        Rights: {active_rights_pct*100:.0f}%
        Composite: ${composite_rate:,.2f}
        + Fringes (Hol/Super)
        EST TOTAL: ${grand_total_weekly:,.2f}
        """
    else:
        summary = f"""
        DEAL MEMO (ATPA - Daily - {performer_class})
        -------------------------
        Basis: {daily_hours} Hour Day
        BNF: ${bnf_daily:,.2f}
        Rights: {active_rights_pct_daily*100:.0f}%
        Composite: ${composite_daily:,.2f}
        Rehearsals: ${rehearsal_cost:,.2f}
        EST TOTAL: ${grand_total_daily:,.2f}
        """
    st.code(summary, language="text")
