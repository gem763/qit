from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.dashboard, name='dashboard'),
    path('run_backtest/', v.RunBacktestView.as_view(), name='run_backtest')
]
