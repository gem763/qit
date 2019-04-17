from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from backtester.utils import run_backtest

def dashboard(request):
    # return HttpResponse(123)
    bt = run_backtest()
    navs = bt.navs()
    navs_model = list(navs['Model'].values)
    navs_bm = list(navs['BM'].values)
    navs_min = max(round(navs.min().min(), 1) - 0.1, 0)
    dates = list(navs.index.date.astype(str))
    results = {'navs_model':navs_model, 'navs_bm':navs_bm, 'dates':dates, 'navs_min':navs_min}
    return render(request, 'backtester/dashboard.html', {'results':results})
