import numpy as np
import pandas as pd
from src.risk_evaluator import PortfolioRiskEvaluator

def test_risk_metrics_logical_order():
    """
    تست منطق ریاضی: CVaR باید همیشه کوچکتر یا مساوی VaR باشد، 
    و VaR باید کوچکتر از میانگین درآمد باشد.
    """
    # ساخت داده‌های فرضی برای تست (Mock Data)
    np.random.seed(42)
    df_test = pd.DataFrame({
        'Solar_Asset': np.random.normal(1200, 400, 500),
        'Battery_Asset': np.random.normal(800, 150, 500)
    })
    
    # راه‌اندازی کلاس با اطمینان ۹۵٪
    evaluator = PortfolioRiskEvaluator(historical_data=df_test, confidence_level=0.95)
    results = evaluator.run_monte_carlo(num_simulations=5000)
    
    # 1. آیا خروجی‌ها نال (Null) نیستند؟
    assert results["mean_expected_revenue"] is not None
    assert results["VaR"] is not None
    assert results["CVaR"] is not None
    
    # 2. تست اصول مالی ریسک (CVaR < VaR < Mean)
    assert results["CVaR"] <= results["VaR"], "CVaR cannot be strictly greater than VaR!"
    assert results["VaR"] < results["mean_expected_revenue"], "VaR should be less than the mean expected revenue!"

def test_confidence_level_impact():
    """
    تست اینکه آیا افزایش سطح اطمینان باعث کاهش عدد VaR (بدبینانه‌تر شدن) می‌شود؟
    """
    np.random.seed(42)
    df_test = pd.DataFrame({'Asset_1': np.random.normal(100, 20, 500)})
    
    eval_90 = PortfolioRiskEvaluator(df_test, confidence_level=0.90)
    eval_99 = PortfolioRiskEvaluator(df_test, confidence_level=0.99)
    
    res_90 = eval_90.run_monte_carlo(num_simulations=2000)
    res_99 = eval_99.run_monte_carlo(num_simulations=2000)
    
    # ریسک ۹۹٪ باید آستانه درآمد پایین‌تری نسبت به ۹۰٪ نشان دهد (محافظه‌کارانه‌تر)
    assert res_99["VaR"] < res_90["VaR"]
