from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from backtester.utils import run_backtest

def dashboard(request):
    # return HttpResponse(123)
    bt = run_backtest()
    navs = bt.navs()
    navs_strat = navs['Strategy'].values
    return render(request, 'backtester/dashboard.html', {'results':navs_strat})
