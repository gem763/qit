from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from backtester.utils import backtest, 매출상위, 매출상위다시, 시총상위PB저평가


model_matcher = {
    0: {'model':매출상위, 'desc':'매출액이 큰 종목'},
    1: {'model':매출상위다시, 'desc':'매출액이 큰 종목2'},
    2: {'model':시총상위PB저평가, 'desc':'시가총액 상위종목 중 PBR이 낮은 종목'},
}


def dashboard(request):
    return render(request, 'backtester/dashboard.html', {'model_matcher':model_matcher})


def get_results(model, n):
    bt = backtest(model, n)
    navs = bt.navs()
    navs_model = list(navs['Model'].values)
    navs_bm = list(navs['BM'].values)
    navs_min = max(round(navs.min().min(), 1) - 0.1, 0)
    stats = bt.stats().T.to_dict('split')
    dates = list(navs.index.date.astype(str))
    pos = bt.position_mapped()
    results = {'navs_model':navs_model, 'navs_bm':navs_bm, 'dates':dates, 'navs_min':navs_min, 'stats':stats, 'pos':pos}
    return results


class RunBacktestView(View):
    def get(self, request):
        model_id = request.GET.get('model_id', None)
        n_pos = request.GET.get('n_pos', None)

        if (model_id is not None) & (n_pos is not None):
            model = model_matcher[int(model_id)]['model']
            n_pos = int(n_pos)
            results = get_results(model, n=n_pos)
            return JsonResponse(results)
