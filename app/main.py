import streamlit as st
import sys
import os

# Ensure we can import from the current directory and subdirectories
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'quant_b_module'))
sys.path.append(os.path.join(current_dir, 'quant_a_module'))

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Asset Management Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- IMPORT MODULES ---
try:
    from quant_b_module.dashboard_b import run_quant_b_dashboard
except ImportError as e:
    st.error(f"Error importing Quant B: {e}")

try:
    from dashboard_a import run_quant_a_dashboard
except ImportError:
    # Fallback if the file rename didn't happen
    def run_quant_a_dashboard():
        st.warning("Quant A Module not found.")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
module = st.sidebar.radio(
    "Select Module:",
    ["Home", "Quant A: Single Asset", "Quant B: Portfolio"]
)

# --- MAIN ROUTING ---
if module == "Home":
    st.title("🏦 Quantitative Research Platform")
    
    # INDENTATION IS CRITICAL HERE
    st.markdown("""
    **Welcome to the Integrated Asset Management Dashboard.**
    
    Please select a module from the sidebar to begin:
    
    * **Quant A (Single Asset):** Focuses on univariate analysis and backtesting strategies.
    * **Quant B (Portfolio):** Focuses on multivariate optimization, correlation, and diversification.
    """)
    
    st.success("System Status: Online 🟢")

elif module == "Quant A: Single Asset":
    run_quant_a_dashboard()

elif module == "Quant B: Portfolio":
    run_quant_b_dashboard()
