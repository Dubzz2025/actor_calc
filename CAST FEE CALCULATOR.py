{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
\
# --- 1. CONFIG & STYLING ---\
st.set_page_config(\
    page_title="ATPA Cast Calc",\
    page_icon="\uc0\u55356 \u57261 ",\
    layout="wide",\
    initial_sidebar_state="expanded"\
)\
\
# Custom CSS for the "Total" cards\
st.markdown("""\
    <style>\
    .metric-card \{\
        background-color: #f0f2f6;\
        border-radius: 10px;\
        padding: 20px;\
        text-align: center;\
        border: 1px solid #dcdcdc;\
    \}\
    .big-number \{\
        font-size: 32px;\
        font-weight: bold;\
        color: #2e7d32;\
    \}\
    .sub-label \{\
        font-size: 14px;\
        color: #555;\
    \}\
    </style>\
""", unsafe_allow_html=True)\
\
st.title("\uc0\u55356 \u57261  ATPA Actor Deal Calculator")\
\
# --- 2. SIDEBAR - GLOBAL SETTINGS ---\
with st.sidebar:\
    st.header("Deal Parameters")\
    \
    agreement = st.selectbox("Agreement", ["ATPA (TV)", "AFFCA (Film)"], index=0)\
    performer_class = st.radio("Performer Class", ["Class 1", "Class 2"], horizontal=True)\
    \
    # Placeholder Minimums (You can update these defaults)\
    # NOTE: These are hypothetical 2024/25 rates. \
    # You would update these to match the exact current MEAA sheet.\
    if agreement == "ATPA (TV)":\
        min_weekly_1 = 1250.00 \
        min_weekly_2 = 1100.00\
        min_daily_1 = 350.00\
        min_daily_2 = 300.00\
    else:\
        min_weekly_1 = 1350.00\
        min_weekly_2 = 1200.00\
        min_daily_1 = 400.00\
        min_daily_2 = 350.00\
\
    current_min_weekly = min_weekly_1 if performer_class == "Class 1" else min_weekly_2\
    current_min_daily = min_daily_1 if performer_class == "Class 1" else min_daily_2\
\
    st.divider()\
    \
    st.subheader("Global Fringes")\
    super_rate = st.number_input("Superannuation %", value=12.0, step=0.5) / 100\
\
# --- 3. MAIN CALCULATOR (TABS) ---\
tab_weekly, tab_daily = st.tabs(["\uc0\u55357 \u56517  Weekly Deal", "\u9728 \u65039  Daily Deal"])\
\
# ==========================================\
#          WEEKLY CALCULATOR\
# ==========================================\
with tab_weekly:\
    col1, col2 = st.columns([1, 1.5])\
    \
    with col1:\
        st.subheader("1. Base Inputs")\
        \
        # Hours Selection\
        weekly_hours = st.selectbox("Weekly Hours", [40, 50, 60], index=1, help="Used for Holiday Pay calculation")\
        \
        # Rate Build\
        base_award = st.number_input("Weekly Award Minimum ($)", value=current_min_weekly, step=10.0)\
        personal_margin = st.number_input("Personal Margin ($)", value=0.0, step=50.0, help="Amount negotiated above minimum")\
        \
        # BNF Calculation\
        bnf_weekly = base_award + personal_margin\
        st.info(f"**BNF (Basic Negotiated Fee):** $\{bnf_weekly:,.2f\}")\
        \
        st.subheader("2. Loadings & Rights")\
        st.caption("Select Applicable Rights:")\
        \
        # Rights Checkboxes (Percentages)\
        rights_config = \{\
            "Aus Free TV (x4) OR (x5) (25%)": 0.25,\
            "World Free/Pay TV (ex US) (25%)": 0.25,\
            "World Theatrical (25%)": 0.25,\
            "World Ancillary (ex Aust) (20%)": 0.20,\
            "Aus Ancillary & Pay TV (20%)": 0.20\
        \}\
        \
        active_rights_pct = 0.0\
        \
        for label, pct in rights_config.items():\
            if st.checkbox(label, key=f"wk_\{label\}"):\
                active_rights_pct += pct\
        \
        # Specific Logic from Prompt: "Composite Rate"\
        # Prompt implies Composite is BNF + Loadings.\
        # However, one line said "Composite Rate 115%". \
        # I assume this means Base (100%) + Loadings. \
        # If user ticks nothing, it's 100%. \
        \
        rights_amount = bnf_weekly * active_rights_pct\
        composite_rate = bnf_weekly + rights_amount\
\
        st.subheader("3. Overtime")\
        ot_amount = st.number_input("Overtime / 6th Day ($)", value=0.0, step=100.0, key="wk_ot")\
\
    # --- WEEKLY CALCULATIONS ---\
    # Formula provided: Composite Rate \'f7 40 \'d7 50 \'f7 12\
    # Note: This formula explicitly scales to 50 hours before dividing by 12.\
    holiday_pay = (composite_rate / 40 * 50) / 12\
    \
    # Formula provided: Total Fee x 12% (Super)\
    # Total Fee usually implies Composite + OT? \
    # Let's assume Total Fee = Composite + OT for Super purposes.\
    total_fee_pre_fringe = composite_rate + ot_amount\
    super_amount = total_fee_pre_fringe * super_rate\
    \
    grand_total_weekly = total_fee_pre_fringe + holiday_pay + super_amount\
\
    # --- WEEKLY OUTPUT ---\
    with col2:\
        st.markdown("### \uc0\u55357 \u56496  Cost Breakdown")\
        \
        # Display as a clean invoice/table\
        line_items = \{\
            "Weekly Award": base_award,\
            "Personal Margin": personal_margin,\
            "\uc0\u10145 \u65039  BNF (Subtotal)": bnf_weekly,\
            f"Rights Loadings (\{active_rights_pct*100:.0f\}%)": rights_amount,\
            "\uc0\u10145 \u65039  Composite Rate": composite_rate,\
            "Overtime/6th Day": ot_amount,\
            "\uc0\u10145 \u65039  Total Fee (Gross)": total_fee_pre_fringe,\
            "Holiday Pay (Comp/40*50/12)": holiday_pay,\
            f"Superannuation (\{super_rate*100\}%)": super_amount\
        \}\
        \
        # Render the lines\
        for k, v in line_items.items():\
            c_a, c_b = st.columns([3, 1])\
            if "\uc0\u10145 \u65039 " in k:\
                c_a.markdown(f"**\{k\}**")\
                c_b.markdown(f"**$\{v:,.2f\}**")\
            else:\
                c_a.write(k)\
                c_b.write(f"$\{v:,.2f\}")\
        \
        st.divider()\
        \
        # Big Total Card\
        st.markdown(f"""\
        <div class="metric-card">\
            <div class="sub-label">Est. Total Cost to Production (Weekly)</div>\
            <div class="big-number">$\{grand_total_weekly:,.2f\}</div>\
        </div>\
        """, unsafe_allow_html=True)\
\
\
# ==========================================\
#          DAILY CALCULATOR\
# ==========================================\
with tab_daily:\
    d_col1, d_col2 = st.columns([1, 1.5])\
    \
    with d_col1:\
        st.subheader("1. Base Inputs")\
        daily_hours = st.selectbox("Daily Hours", [8, 10], index=1)\
        \
        base_award_daily = st.number_input("Daily Award Minimum ($)", value=current_min_daily, step=10.0, key="d_award")\
        margin_daily = st.number_input("Personal Margin ($)", value=0.0, step=50.0, key="d_margin")\
        \
        bnf_daily = base_award_daily + margin_daily\
        st.info(f"**BNF (Daily):** $\{bnf_daily:,.2f\}")\
        \
        st.subheader("2. Loadings & Rehearsals")\
        \
        # Rehearsal Logic\
        # Formula: (BNF / 8) * Hours\
        rehearsal_hours = st.number_input("Rehearsal Hours", min_value=0.0, step=0.5)\
        rehearsal_cost = 0.0\
        if rehearsal_hours > 0:\
            rehearsal_cost = (bnf_daily / 8) * rehearsal_hours\
            if rehearsal_hours < 2.5:\
                st.warning("\uc0\u9888 \u65039  Standard minimum call is usually 2.5hrs")\
        \
        st.caption("Applicable Rights:")\
        active_rights_pct_daily = 0.0\
        for label, pct in rights_config.items():\
            if st.checkbox(label, key=f"day_\{label\}"):\
                active_rights_pct_daily += pct\
                \
        rights_amt_daily = bnf_daily * active_rights_pct_daily\
        composite_daily = bnf_daily + rights_amt_daily + rehearsal_cost\
\
        st.subheader("3. Overtime")\
        ot_hours_daily = st.number_input("OT Hours", value=0.0, step=0.5)\
        # Simple OT calc placeholder (User can overwrite amount if needed, or we add logic)\
        # For now, let's just ask for the amount to be safe, or estimate based on 1.5x\
        # Let's calculate a rough estimate based on BNF/8\
        hourly_rate = bnf_daily / 8\
        est_ot_cost = (hourly_rate * 1.5 * 2) + (hourly_rate * 2.0 * (ot_hours_daily - 2)) if ot_hours_daily > 2 else (hourly_rate * 1.5 * ot_hours_daily)\
        \
        ot_amt_daily = st.number_input("Overtime Amount ($)", value=est_ot_cost if ot_hours_daily > 0 else 0.0, step=50.0)\
\
    # --- DAILY CALCULATIONS ---\
    # Assuming same Holiday Pay logic applies? (Scaled to 50 hr week equivalent?)\
    # Usually daily holiday pay is just 1/12th of total. \
    # BUT, to stick to your specific prompt's logic flow, I will use the \
    # pro-rata equivalent or just standard 8.33% (1/12) of the Composite.\
    \
    # Prompt didn't specify distinct Daily Holiday formula, usually it's 1/12 of negotiated fee.\
    holiday_pay_daily = composite_daily / 12 \
    \
    total_daily_pre_fringe = composite_daily + ot_amt_daily\
    super_daily = total_daily_pre_fringe * super_rate\
    \
    grand_total_daily = total_daily_pre_fringe + holiday_pay_daily + super_daily\
\
    # --- DAILY OUTPUT ---\
    with d_col2:\
        st.markdown("### \uc0\u55357 \u56496  Cost Breakdown (Daily)")\
        \
        line_items_d = \{\
            "Daily Award": base_award_daily,\
            "Personal Margin": margin_daily,\
            "\uc0\u10145 \u65039  BNF": bnf_daily,\
            f"Rehearsals (\{rehearsal_hours\}hrs)": rehearsal_cost,\
            f"Rights Loadings (\{active_rights_pct_daily*100:.0f\}%)": rights_amt_daily,\
            "\uc0\u10145 \u65039  Composite Rate": composite_daily,\
            f"Overtime (\{ot_hours_daily\}hrs)": ot_amt_daily,\
            "\uc0\u10145 \u65039  Total Fee (Gross)": total_daily_pre_fringe,\
            "Holiday Pay (1/12th)": holiday_pay_daily,\
            f"Superannuation (\{super_rate*100\}%)": super_daily\
        \}\
        \
        for k, v in line_items_d.items():\
            c_a, c_b = st.columns([3, 1])\
            if "\uc0\u10145 \u65039 " in k:\
                c_a.markdown(f"**\{k\}**")\
                c_b.markdown(f"**$\{v:,.2f\}**")\
            else:\
                c_a.write(k)\
                c_b.write(f"$\{v:,.2f\}")\
                \
        st.divider()\
        st.markdown(f"""\
        <div class="metric-card">\
            <div class="sub-label">Est. Total Cost to Production (Daily)</div>\
            <div class="big-number">$\{grand_total_daily:,.2f\}</div>\
        </div>\
        """, unsafe_allow_html=True)\
\
# --- 4. EXPORT / COPY ---\
st.divider()\
if st.button("\uc0\u55357 \u56541  Copy Deal Points"):\
    # This generates a text block you can copy\
    if tab_weekly:\
        summary = f"""\
        DEAL MEMO (ATPA - \{performer_class\})\
        -------------------------\
        Basis: \{weekly_hours\} Hour Week\
        BNF: $\{bnf_weekly:,.2f\} (Base $\{base_award\} + Margin $\{personal_margin\})\
        Rights: \{active_rights_pct*100:.0f\}%\
        Composite: $\{composite_rate:,.2f\}\
        + Fringes (Hol/Super)\
        EST TOTAL: $\{grand_total_weekly:,.2f\}\
        """\
    else:\
        summary = f"""\
        DEAL MEMO (ATPA - Daily - \{performer_class\})\
        -------------------------\
        Basis: \{daily_hours\} Hour Day\
        BNF: $\{bnf_daily:,.2f\}\
        Rights: \{active_rights_pct_daily*100:.0f\}%\
        Composite: $\{composite_daily:,.2f\}\
        EST TOTAL: $\{grand_total_daily:,.2f\}\
        """\
    st.code(summary, language="text")}