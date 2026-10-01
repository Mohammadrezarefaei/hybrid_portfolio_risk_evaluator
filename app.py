import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Hybrid Portfolio Risk & CVaR", layout="wide")

st.title("🛡️ Hybrid Asset Portfolio Risk & CVaR Evaluator")
st.markdown("Monte Carlo simulation for evaluating the financial risk of a hybrid asset portfolio (Solar + BESS) participating in Day-Ahead and aFRR markets.")

# Sidebar Settings
st.sidebar.header("Simulation Parameters")
confidence_level = st.sidebar.slider("Confidence Level", min_value=0.90, max_value=0.99, value=0.95, step=0.01)
num_simulations = st.sidebar.number_input("Number of Monte Carlo Scenarios", min_value=1000, max_value=50000, value=10000, step=1000)

st.sidebar.subheader("Market Parameters (Mean Daily Revenue - €)")
solar_mean = st.sidebar.number_input("Solar (Day-Ahead)", value=1200)
bess_arb_mean = st.sidebar.number_input("Battery (Arbitrage)", value=500)
bess_afrr_mean = st.sidebar.number_input("Battery (aFRR)", value=800)

st.sidebar.subheader("Market Volatility (Standard Deviation)")
solar_std = st.sidebar.slider("Solar Volatility", 100, 1000, 400)
bess_arb_std = st.sidebar.slider("Arbitrage Volatility", 50, 500, 200)
bess_afrr_std = st.sidebar.slider("aFRR Volatility", 50, 500, 150)

# 1. Generate Base Data and Covariance Matrix
np.random.seed(42)
days = 365
df_historical = pd.DataFrame({
    'Solar_DA': np.random.normal(solar_mean, solar_std, days),
    'BESS_Arbitrage': np.random.normal(bess_arb_mean, bess_arb_std, days),
    'BESS_aFRR': np.random.normal(bess_afrr_mean, bess_afrr_std, days)
})

mean_returns = df_historical.mean()
cov_matrix = df_historical.cov()

# 2. Run Monte Carlo Simulation
simulated_revenues = np.random.multivariate_normal(mean_returns, cov_matrix, num_simulations)
portfolio_simulated_rev = np.sum(simulated_revenues, axis=1)

# 3. Calculate Risk Metrics
sorted_revenues = np.sort(portfolio_simulated_rev)
index_at_risk = int((1 - confidence_level) * num_simulations)

VaR = sorted_revenues[index_at_risk]
CVaR = sorted_revenues[:index_at_risk].mean()
mean_expected = portfolio_simulated_rev.mean()
max_loss = mean_expected - CVaR

# Display Metrics Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Mean Expected Revenue", f"€{mean_expected:,.0f}")
col2.metric(f"VaR ({int(confidence_level*100)}%)", f"€{VaR:,.0f}", "Risk Threshold", delta_color="inverse")
col3.metric(f"CVaR ({int(confidence_level*100)}%)", f"€{CVaR:,.0f}", "Average in Worst-Case", delta_color="inverse")
col4.metric("Max Potential Loss", f"€{max_loss:,.0f}")

st.divider()

# 4. Plot Risk Distribution
fig, ax = plt.subplots(figsize=(12, 5))
plt.style.use('seaborn-v0_8-whitegrid')

sns.histplot(portfolio_simulated_rev, bins=100, kde=True, color='skyblue', stat='density', ax=ax)

ax.axvline(mean_expected, color='green', linestyle='dashed', linewidth=2, label=f'Mean Expected: €{mean_expected:,.0f}')
ax.axvline(VaR, color='orange', linestyle='dashed', linewidth=2, label=f'VaR: €{VaR:,.0f}')
ax.axvline(CVaR, color='red', linestyle='dashed', linewidth=2, label=f'CVaR: €{CVaR:,.0f}')

kde_x, kde_y = ax.lines[0].get_data()
ax.fill_between(kde_x, kde_y, where=(kde_x < VaR), color='red', alpha=0.3, label=f'Tail Risk (Worst {int((1-confidence_level)*100)}%)')

ax.set_title(f'Portfolio Daily Revenue Distribution ({num_simulations:,} Monte Carlo Scenarios)', fontsize=14)
ax.set_xlabel('Simulated Daily Revenue (€)', fontsize=12)
ax.set_ylabel('Density', fontsize=12)
ax.legend(loc='upper right')

st.pyplot(fig)
