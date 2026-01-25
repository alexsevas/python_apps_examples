# ArviZ — специализированная библиотека для исследования и визуализации результатов байесовского моделирования.
# Она работает в связке с Python-фреймворками для вероятностного программирования, такими как PyMC, Stan, Pyro
# и другими,  облегчая анализ MCMC-сэмплов, диагностику и визуальный отчёт.
#
# pip install arviz
#
# Пример использования:


import arviz as az
import pymc as pm

with pm.Model() as model:
    α = pm.Normal("α", 0, 1)
    β = pm.Normal("β", 0, 1)
    σ = pm.HalfNormal("σ", 1)
    μ = α + β * pm.Data("x", [1,2,3,4,5])
    y = pm.Normal("y", μ, σ, observed=[1.2,1.9,2.8,4.1,4.9])
    idata = pm.sample(return_inferencedata=True)

# Cводка результатов
print(az.summary(idata, var_names=["α", "β", "σ"]))

# Трассировка параметров и автокорреляции
az.plot_trace(idata, var_names=["α", "β"])
