import numpy as np
import pandas as pd

class PortfolioRiskEvaluator:
    """
    محاسبه ریسک پورتفولیو (VaR و CVaR) با استفاده از شبیه‌سازی مونت‌کارلو
    """
    def __init__(self, historical_data: pd.DataFrame, confidence_level: float = 0.95):
        self.historical_data = historical_data
        self.confidence_level = confidence_level
        
    def run_monte_carlo(self, num_simulations: int = 10000):
        # استخراج میانگین و ماتریس کوواریانس از داده‌های تاریخی
        mean_returns = self.historical_data.mean()
        cov_matrix = self.historical_data.cov()
        
        # تولید سناریوهای تصادفی بر اساس توزیع نرمال چندمتغیره
        simulated_revenues = np.random.multivariate_normal(
            mean_returns, cov_matrix, num_simulations
        )
        
        # جمع درآمدهای دارایی‌ها برای رسیدن به درآمد کل پورتفولیو در هر سناریو
        portfolio_simulated_rev = np.sum(simulated_revenues, axis=1)
        
        # مرتب‌سازی برای محاسبه صدک‌ها
        sorted_rev = np.sort(portfolio_simulated_rev)
        index_at_risk = int((1 - self.confidence_level) * num_simulations)
        
        var = sorted_rev[index_at_risk]
        cvar = sorted_rev[:index_at_risk].mean()
        mean_expected = portfolio_simulated_rev.mean()
        
        return {
            "mean_expected_revenue": mean_expected,
            "VaR": var,
            "CVaR": cvar,
            "simulated_revenues_distribution": portfolio_simulated_rev
        }
