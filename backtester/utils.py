from django.conf import settings
import pandas as pd
import os


info_path = os.path.join(settings.BASE_DIR, 'info.pkl')
fin_path = os.path.join(settings.BASE_DIR, 'fin.pkl')
mc_path = os.path.join(settings.BASE_DIR, 'mc.pkl')

info = pd.read_pickle(info_path)
fin = pd.read_pickle(fin_path)
mc = pd.read_pickle(mc_path)


def run_backtest():
    bt = Backtest(strat=mcTopLowPB, bm=BM, fin=fin, mc=mc, n=10)
    bt.run()
    return bt


def get_fisyear(date):
    if type(date)==str:
        date = pd.Timestamp(date)

    if date.month >= 6:
        return date.year - 1

    else:
        return date.year - 2


def salesTop10(date, fin=None, mc=None, n=10):
    fisyear = get_fisyear(date)
    position = fin['매출액'].xs(fisyear, level=1).nlargest(n)
    position[:] = 1/len(position)
    return position


def salesTop10_2(date, fin=None, mc=None, n=10):
    fisyear = get_fisyear(date)
    univ = mc.columns[mc.loc[date]>0]
    position = fin['매출액'].xs(fisyear, level=1).loc[univ].nlargest(n)
    position[:] = 1/len(position)
    return position

def mcTopLowPB(date, fin=None, mc=None, n=10):
    fisyear = get_fisyear(date)
    marketcap = mc.loc[date].nlargest(100)
    univ = marketcap.index
    bv = fin['자본총계'].xs(fisyear, level=1).loc[univ]
    bp = bv / marketcap
    position = bp.nlargest(n)
    position[:] = 1/len(position)
    return position


def BM(date, fin=None, mc=None, n=200):
    position = mc.loc[date].nlargest(n)
    position /= position.sum()
    return position



class Backtest:
    def __init__(self, strat=None, bm=None, fin=None, mc=None, n=10):
        self.strat = strat
        self.bm = bm
        self.fin = fin
        self.mc = mc
        self.n = n

    def run(self):
        dates = self.mc.index[8:]
        pos = {}
        nav = {}
        pos_bm = {}
        nav_bm = {}

        for i,date in enumerate(dates):
            pos[date] = self.strat(date, fin=self.fin, mc=self.mc, n=self.n)
            pos_bm[date] = self.bm(date, fin=self.fin, mc=self.mc)

            if i==0:
                nav[date] = 1
                nav_bm[date] = 1

            else:
                date_prev = dates[i-1]
                nav[date] = self.evaluate(nav, pos, date_prev, date)
                nav_bm[date] = self.evaluate(nav_bm, pos_bm, date_prev, date)

        self.nav = nav
        self.pos = pos
        self.nav_bm = nav_bm
        self.pos_bm = pos_bm


    def evaluate(self, nav, pos, date_prev, date):
        nav_prev = nav[date_prev]
        pos_prev = pos[date_prev]
        assets_prev = pos_prev.index
        pos_update = self.mc.loc[date, assets_prev] / self.mc.loc[date_prev, assets_prev] * pos_prev
        return nav_prev * pos_update.sum()

    def navs(self):
        return pd.DataFrame({'Model':self.nav, 'BM':self.nav_bm})

    def plot_perf(self):
        self.navs().plot()

    def stats(self):
        _navs = self.navs()
        days_all = (_navs.index[-1]-_navs.index[0]).days
        ann_rtn = (_navs.iloc[-1]**(365/days_all))-1
        vol = _navs.pct_change().std() * 4**0.5
        return pd.DataFrame({'연수익률':ann_rtn, '변동성':vol, '샤프':ann_rtn/vol})

    def position(self, date=None, what='strat'):
        if what=='strat':
            pos = self.pos
        elif what=='bm':
            pos = self.pos_bm

        if date is None:
            return pd.DataFrame(pos).T
        else:
            return pos[pd.Timestamp(date)]
