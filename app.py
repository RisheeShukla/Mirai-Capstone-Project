import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import io
from datetime import datetime, timedelta
import google.generativeai as genai
from gtts import gTTS

st.set_page_config(
    page_title="RoastMySpend — Brutal AI Expense Auditor",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .metric-card {
        background-color: #1e222d;
        border: 1px solid #313746;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    .roast-container {
        background-color: #2b1114;
        border-left: 5px solid #ff4b4b;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

if "expense_df" not in st.session_state:
    st.session_state.expense_df = None
if "roast_result" not in st.session_state:
    st.session_state.roast_result = None
if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = False
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

def generate_sample_data():
    categories = {
        "Dining & Delivery": ["Swiggy", "Zomato", "Starbucks", "Fine Dine Sushi"],
        "Entertainment & Subscriptions": ["Netflix", "Spotify", "Steam Sale", "Gym Membership (Unused)"],
        "Shopping & Impulse": ["Sneakers", "Mechanical Keyboard", "Amazon Random Gadget"],
        "Groceries & Essentials": ["Supermarket", "Pharmacy", "Utility Bill", "Wifi"],
        "Commute & Travel": ["Uber Surge", "Gas Station", "Flight Tickets"]
    }
    
    data = []
    base_date = datetime.now() - timedelta(days=30)
    
    np.random.seed(42)
    for i in range(40):
        cat = np.random.choice(list(categories.keys()), p=[0.35, 0.20, 0.20, 0.15, 0.10])
        item = np.random.choice(categories[cat])
        amount = round(np.random.exponential(scale=650) + 120, 2)
        date = (base_date + timedelta(days=int(np.random.uniform(0, 30)))).strftime("%Y-%m-%d")
        is_discretionary = cat not in ["Groceries & Essentials"]
        data.append({"Date": date, "Description": item, "Category": cat, "Amount": amount, "Discretionary": is_discretionary})
    
    df = pd.DataFrame(data).sort_values("Date").reset_index(drop=True)
    return df

def categorize_and_clean(df):
    required_cols = {"Date", "Description", "Category", "Amount"}
    if not required_cols.issubset(set(df.columns)):
        raise ValueError(f"Uploaded CSV must contain columns: {', '.join(required_cols)}")
    
    df["Date"] = pd.to_datetime(df["Date"])
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    
    if "Discretionary" not in df.columns:
        essential_keywords = ["grocery", "groceries", "utility", "rent", "pharmacy", "medical", "bill", "wifi"]
        df["Discretionary"] = ~df["Category"].str.lower().isin(essential_keywords)
    
    return df.sort_values("Date").reset_index(drop=True)

def generate_audio_summary(roast_text):
    """Converts a short AI summary into playable audio bytes."""
    tts = gTTS(text=roast_text, lang='en', tld='com', slow=False)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer


with st.sidebar:
    st.title("🔥 Roast Settings")
    st.caption("Configure AI Auditor Personality & Telemetry")
    
    api_key_input = st.text_input("Enter Gemini API Key", type="password", help="Grab your key from Google AI Studio")
    if api_key_input:
        genai.configure(api_key=api_key_input)
        st.session_state.api_key_configured = True
        st.success("API Key Active")
    
    st.divider()
    
    persona = st.selectbox(
        "Roaster Persona",
        [
            "Ruthless Wall Street Quant",
            "Disappointed Desi / Traditional Parent",
            "Silicon Valley VC / Burn-Rate Obsessed CFO",
            "Gordon Ramsay of Personal Finance"
        ],
        index=0
    )
    
    roast_intensity = st.select_slider(
        "Roast Intensity",
        options=["Mild Sarcasm", "Painful Reality Check", "Nuclear Emotional Damage"],
        value="Nuclear Emotional Damage"
    )
    
    monthly_income_target = st.number_input("Your Net Monthly Income ($ / ₹)", min_value=1000, value=65000, step=1000)

st.title("💸 The Expense Roaster & Recovery Engine")
st.markdown("Upload your mock/real expenses, review automated discretionary leak audits, and let Gemini brutally restructure your personal cash flow.")

tab_upload, tab_analytics, tab_roast = st.tabs(["1. Data Ingestion & Live Editor", "2. Financial Telemetry & Leak Visuals", "3. AI Roast & Recovery Plan"])


with tab_upload:
    col_u1, col_u2 = st.columns([2, 1])
    
    with col_u1:
        uploaded_file = st.file_uploader("Upload Monthly Expense CSV", type=["csv"])
        if uploaded_file:
            try:
                raw_df = pd.read_csv(uploaded_file)
                st.session_state.expense_df = categorize_and_clean(raw_df)
                st.success("CSV Loaded & Cleaned Successfully!")
            except Exception as e:
                st.error(f"Error parsing CSV: {e}")
                
    with col_u2:
        st.write("#### Or test instantly:")
        if st.button("📥 Load Sample Chaotic Spending Dataset", use_container_width=True):
            st.session_state.expense_df = generate_sample_data()
            st.success("Loaded 40 transaction mock records!")

    if st.session_state.expense_df is not None:
        st.subheader("Interactive Transaction Editor")
        st.caption("Double click to tweak transactions live before triggering analysis.")
        edited_df = st.data_editor(
            st.session_state.expense_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Amount": st.column_config.NumberColumn(format="%.2f"),
                "Discretionary": st.column_config.CheckboxColumn("Discretionary (Leak)")
            }
        )
        st.session_state.expense_df = edited_df


with tab_analytics:
    if st.session_state.expense_df is None:
        st.info("Please upload a CSV or load the sample dataset in Tab 1 first.")
    else:
        df = st.session_state.expense_df.copy()
        
        total_spend = df["Amount"].sum()
        discretionary_spend = df[df["Discretionary"] == True]["Amount"].sum()
        essential_spend = total_spend - discretionary_spend
        savings_left = monthly_income_target - total_spend
        
        ideal_disc = monthly_income_target * 0.30
        disc_delta = discretionary_spend - ideal_disc

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Monthly Burn", f"{total_spend:,.2f}", delta=f"{(total_spend/monthly_income_target)*100:.1f}% of Income", delta_color="inverse")
        k2.metric("Discretionary Leaks", f"{discretionary_spend:,.2f}", delta=f"{disc_delta:+,.2f} vs 30% Ideal", delta_color="inverse")
        k3.metric("Essential Baseline", f"{essential_spend:,.2f}", delta=f"{(essential_spend/total_spend)*100:.1f}% Total Burn", delta_color="off")
        k4.metric("Net Surplus / Deficit", f"{savings_left:,.2f}", delta=f"Target: {monthly_income_target*0.20:,.2f} min savings", delta_color="normal" if savings_left >= (monthly_income_target*0.20) else "inverse")

        st.divider()
        
        c_chart1, c_chart2 = st.columns([1, 1])
        
        with c_chart1:
            st.markdown("##### Spending Breakdown by Category")
            cat_summary = df.groupby("Category")["Amount"].sum().reset_index()
            fig_pie = px.pie(
                cat_summary, 
                values="Amount", 
                names="Category", 
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c_chart2:
            st.markdown("##### Cumulative Daily Burn Velocity")
            df_sorted = df.sort_values("Date").copy()
            df_sorted["Cumulative"] = df_sorted["Amount"].cumsum()
            fig_line = px.area(
                df_sorted, 
                x="Date", 
                y="Cumulative", 
                labels={"Cumulative": "Total Burned"},
                color_discrete_sequence=["#ff4b4b"]
            )
            fig_line.add_hline(y=monthly_income_target, line_dash="dash", line_color="yellow", annotation_text="Monthly Income Cap")
            fig_line.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_line, use_container_width=True)

with tab_roast:
    if st.session_state.expense_df is None:
        st.warning("Upload transaction data first!")
    else:
        df = st.session_state.expense_df
        
        with st.form("roast_generation_form"):
            st.write("### AI Auditor Command Center")
            st.write(f"Auditor Persona: **{persona}** | Intensity: **{roast_intensity}**")
            
            user_excuse = st.text_input("Optional: What is your primary excuse for this month's spending?", placeholder="e.g., 'I was stressed from finals and needed door delivery daily.'")
            
            submit_roast = st.form_submit_button("🔥 Audit & Brutally Roast Spending", use_container_width=True)
            
        if submit_roast:
            total_spend = df["Amount"].sum()
            disc_df = df[df["Discretionary"] == True]
            top_leaks = disc_df.groupby("Description")["Amount"].sum().nlargest(5).to_dict()
            category_totals = df.groupby("Category")["Amount"].sum().to_dict()
            
            prompt_context = f"""
            FINANCIAL PROFILE OF USER:
            - Monthly Net Income: {monthly_income_target}
            - Total Spend This Month: {total_spend}
            - Discretionary Leak Amount: {disc_df['Amount'].sum()}
            - Category Breakdown: {json.dumps(category_totals)}
            - Top 5 Discretionary Money Sinks: {json.dumps(top_leaks)}
            - User's Stated Excuse: "{user_excuse if user_excuse else 'No excuse offered'}"
            """
            
            system_instruction = f"""
            You are an elite, hilarious, and unapologetically brutal personal finance auditor adopting the persona: {persona}.
            Intensity Level: {roast_intensity}.
            
            Your goals:
            1. Deliver a savage, specific roast of their spending habits based on the exact line items, top leaks, and excuse provided.
            2. Assign a 'Financial Survival Grade' from F- to A+.
            3. Highlight the 3 most ridiculous expenses they made.
            4. Provide a realistic, strict '30-Day Budget Recovery Plan' to plug leaks immediately.
            5. Write in high-energy Markdown format with headings, bullet points, and quotes.
            """
            
            with st.spinner("AI Auditor is dissecting your poor life choices..."):
                if not st.session_state.api_key_configured and not os.getenv("GEMINI_API_KEY"):
                    # Mock response for testing without API key
                    st.session_state.roast_result = f"""
                    ### 🚨 AUDIT REPORT: FINANCIAL CRIME SCENE
                    **Financial Survival Grade:** `D- (Critical Runway Depletion)`
                    
                    > *"You spent more on random food deliveries and impulse gadgets than your future self has saved for retirement."*
                    
                  
                    Look at this ledger. You burned **{disc_df['Amount'].sum():,.2f}** on pure impulse gratification. 
                    - Your top money sink includes **{list(top_leaks.keys())[0] if top_leaks else 'Impulse Buys'}**, costing you **{list(top_leaks.values())[0] if top_leaks else 0:,.2f}**.
                    - You told yourself: *"{user_excuse if user_excuse else 'Treat yourself'}."* The only thing you treated was your delivery driver to guaranteed employment!
                    
                    ---
                    #### 🛑 Top 3 Most Ridiculous Leaks
                    1. **Dining Out Surges:** Burning cash when you have groceries expiring at home.
                    2. **Unused Subscriptions:** Micro-transactions silently siphoning compounding interest.
                    3. **Impulse Shopping:** Dopamine hits that will sit in your closet untouched next week.
                    
                    ---
                    #### 🛠️ 30-Day Budget Recovery Sprint
                    - **Immediate Cut (24h):** Delete one-click food delivery apps until your surplus exceeds 20% of net income.
                    - **Rule 72:** Implement a 72-hour mandatory waiting period on any discretionary purchase over 50.
                    - **Target Recovery:** Recapture at least **{(disc_df['Amount'].sum() * 0.4):,.2f}** next month by shifting spending to essentials.
                    """
                    # Generate mock audio summary
                    mock_audio_text = f"You burned {disc_df['Amount'].sum():,.2f} on pure nonsense this month. Stop clicking purchase and make a budget."
                    st.session_state.audio_bytes = generate_audio_summary(mock_audio_text)

                else:
                    try:
                        model = genai.GenerativeModel(
                            model_name="gemini-3.7-flash",
                            system_instruction=system_instruction
                        )
                        # 1. Full Text Roast
                        response = model.generate_content(f"{prompt_context}\nGenerate the complete roast and recovery matrix.")
                        st.session_state.roast_result = response.text
                        
                       
                        audio_prompt = f"Summarize this financial roast in 1 short, brutal sentence to be spoken out loud: {response.text}"
                        audio_response = model.generate_content(audio_prompt)
                        
                      
                        st.session_state.audio_bytes = generate_audio_summary(audio_response.text)
                        
                    except Exception as err:
                        st.error(f"Gemini API Error: {err}")

    
        if st.session_state.roast_result:
            if st.session_state.audio_bytes:
                st.markdown("### 🎧 Listen to your Financial Verdict")
                st.audio(st.session_state.audio_bytes, format="audio/mp3")
                
            st.markdown('<div class="roast-container">', unsafe_allow_html=True)
            st.markdown(st.session_state.roast_result)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.download_button(
                label="📄 Download Recovery Contract (Markdown)",
                data=st.session_state.roast_result,
                file_name=f"financial_recovery_plan_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
