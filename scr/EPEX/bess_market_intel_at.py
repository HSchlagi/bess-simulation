from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict, List

def _to_dt(x):
    return pd.to_datetime(x, utc=True, errors='coerce')
def _coerce_float(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(',', '.', regex=False).str.replace(' ', ''), errors='coerce')
def _normalize_bzn(text: str) -> str:
    return str(text).strip().upper()

@dataclass
class BESSSpec:
    power_mw: float
    energy_mwh: float
    availability: float = 0.97
    degradation_factor: float = 0.95

class EpexIDA:
    def load_csv(self, path: str, market_area: Optional[str] = None) -> pd.DataFrame:
        df = pd.read_csv(path)
        cmap = {}
        for c in df.columns:
            lc = c.lower()
            if 'delivery period start' in lc or 'delivery start' in lc or (lc == 'start'):
                cmap[c] = 'start'
            elif 'delivery period end' in lc or 'delivery end' in lc or (lc == 'end'):
                cmap[c] = 'end'
            elif 'auction' in lc:
                cmap[c] = 'auction'
            elif 'market area' in lc or 'bidding zone' in lc or 'country' in lc or 'bzn' in lc:
                cmap[c] = 'bzn'
            elif 'price' in lc and ('eur/mwh' in lc or '€/mwh' in lc or 'clearing' in lc):
                cmap[c] = 'price_eur_mwh'
        df = df.rename(columns=cmap)
        for r in ['start','end','price_eur_mwh']:
            if r not in df.columns:
                raise ValueError(f"Missing column '{r}' after auto-mapping. Please inspect CSV header.")
        if 'auction' not in df.columns:
            lower = path.lower()
            if 'ida1' in lower: auc = 'IDA1'
            elif 'ida2' in lower: auc = 'IDA2'
            elif 'ida3' in lower: auc = 'IDA3'
            else: auc = 'IDA?'
            df['auction'] = auc
        if 'bzn' not in df.columns:
            df['bzn'] = market_area if market_area else 'AT'
        df['start'] = _to_dt(df['start'])
        df['end'] = _to_dt(df['end'])
        df['bzn'] = df['bzn'].map(_normalize_bzn)
        df['auction'] = df['auction'].astype(str).str.upper()
        df['price_eur_mwh'] = _coerce_float(df['price_eur_mwh'])
        df = df[['bzn','auction','start','end','price_eur_mwh']].sort_values(['start','bzn','auction'])
        return df

    @staticmethod
    def to_quarter_hour(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for _, r in df.iterrows():
            rng = pd.date_range(r['start'], r['end'], inclusive='left', freq='15T')
            for t0 in rng:
                rows.append({'bzn': r['bzn'], 'auction': r['auction'], 'start': t0,
                             'end': t0 + pd.Timedelta(minutes=15), 'price_eur_mwh': r['price_eur_mwh']})
        out = pd.DataFrame(rows)
        return out.sort_values(['start','bzn','auction']).reset_index(drop=True)

class APGRegelenergie:
    def load_capacity(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        cmap = {}
        for c in df.columns:
            lc = c.lower()
            if 'from' in lc or 'start' in lc or 'beginn' in lc or 'date' in lc:
                cmap[c] = 'start'
            elif 'to' in lc or 'end' in lc or 'ende' in lc:
                cmap[c] = 'end'
            elif 'product' in lc or 'art' in lc:
                cmap[c] = 'product'
            elif 'price' in lc and ('eur/mw' in lc or '€/mw' in lc or 'eur per mw' in lc):
                cmap[c] = 'price_eur_per_mw'
        df = df.rename(columns=cmap)
        if 'end' not in df.columns:
            df['end'] = pd.to_datetime(df['start']) + pd.Timedelta(hours=1)
        else:
            df['end'] = pd.to_datetime(df['end'])
        df['start'] = pd.to_datetime(df['start'])
        if 'product' not in df.columns:
            df['product'] = 'aFRR_up'
        df['product'] = df['product'].astype(str).str.strip().str.replace(' ', '').str.lower()
        df['price_eur_per_mw'] = _coerce_float(df['price_eur_per_mw'])
        return df[['start','end','product','price_eur_per_mw']].sort_values('start')

    def load_activation(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        cmap = {}
        for c in df.columns:
            lc = c.lower()
            if 'from' in lc or 'start' in lc or 'beginn' in lc or 'date' in lc:
                cmap[c] = 'start'
            elif 'to' in lc or 'end' in lc or 'ende' in lc:
                cmap[c] = 'end'
            elif 'product' in lc or 'art' in lc:
                cmap[c] = 'product'
            elif 'price' in lc and ('eur/mwh' in lc or '€/mwh' in lc):
                cmap[c] = 'price_eur_per_mwh'
        df = df.rename(columns=cmap)
        if 'price_eur_per_mwh' not in df.columns:
            raise ValueError("Could not detect activation price column (EUR/MWh)")
        if 'end' not in df.columns:
            df['end'] = pd.to_datetime(df['start']) + pd.Timedelta(minutes=15)
        else:
            df['end'] = pd.to_datetime(df['end'])
        df['start'] = pd.to_datetime(df['start'])
        if 'product' not in df.columns:
            df['product'] = 'aFRR_up'
        df['product'] = df['product'].astype(str).str.strip().str.replace(' ', '').str.lower()
        df['price_eur_per_mwh'] = _coerce_float(df['price_eur_per_mwh'])
        return df[['start','end','product','price_eur_per_mwh']].sort_values('start')

def revenue_from_ida(spec: BESSSpec, ida_series_eur_mwh: pd.Series, cycles_per_day: float = 0.2) -> float:
    daily_mwh = spec.energy_mwh * cycles_per_day
    avg_price = np.nanmean(ida_series_eur_mwh.values) if len(ida_series_eur_mwh) else 0.0
    spread_capture = 0.10
    volatility_factor = 0.25
    revenue = daily_mwh * 365.0 * avg_price * spread_capture * volatility_factor
    revenue *= spec.availability * spec.degradation_factor
    return float(revenue)

def revenue_from_capacity(spec: BESSSpec, per_mw_series_eur: pd.Series) -> float:
    total = per_mw_series_eur.fillna(0).sum() * spec.power_mw
    return float(total * spec.availability * spec.degradation_factor)

def revenue_from_activation(spec: BESSSpec, price_eur_mwh: pd.Series, assumed_activation_share: float = 0.05) -> float:
    energy_per_block = spec.energy_mwh * assumed_activation_share
    rev = (price_eur_mwh.fillna(0.0) * energy_per_block).sum()
    rev *= spec.availability * spec.degradation_factor
    return float(rev)

class ATMarketIntegrator:
    def __init__(self, bzn: str = 'AT'):
        self.bzn = _normalize_bzn(bzn)
        self.epex = EpexIDA()
        self.apg = APGRegelenergie()
    def load_ida_csvs(self, paths: List[str]) -> pd.DataFrame:
        frames = [self.epex.load_csv(p, market_area=self.bzn) for p in paths]
        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=['bzn','auction','start','end','price_eur_mwh'])
        return df.sort_values(['start','auction'])
    def ida_quarter_series(self, df_ida: pd.DataFrame) -> pd.Series:
        if df_ida.empty:
            return pd.Series(dtype=float)
        q = self.epex.to_quarter_hour(df_ida)
        order = {'IDA1': 1, 'IDA2': 2, 'IDA3': 3}
        q['rank'] = q['auction'].map(order).fillna(0)
        q = q.sort_values(['start','rank']).drop_duplicates(subset=['start'], keep='last')
        s = q.set_index('start')['price_eur_mwh'].sort_index()
        return s
    def load_apg_capacity(self, path: str, product_filter: Optional[str] = None) -> pd.Series:
        cap = self.apg.load_capacity(path)
        if product_filter:
            cap = cap[cap['product'].str.contains(product_filter.lower())]
        return cap.set_index('start')['price_eur_per_mw'].sort_index()
    def load_apg_activation(self, path: str, product_filter: Optional[str] = None) -> pd.Series:
        act = self.apg.load_activation(path)
        if product_filter:
            act = act[act['product'].str.contains(product_filter.lower())]
        return act.set_index('start')['price_eur_per_mwh'].sort_index()
    def kpis(self, ida_series: Optional[pd.Series]=None,
             cap_series: Optional[pd.Series]=None,
             act_series: Optional[pd.Series]=None,
             spec: Optional[BESSSpec]=None) -> Dict[str, float]:
        spec = spec or BESSSpec(2.0, 8.0)
        out = {}
        if ida_series is not None and len(ida_series):
            out['ida_avg_price_eur_mwh'] = float(ida_series.mean())
            out['ida_p95_eur_mwh'] = float(ida_series.quantile(0.95))
            out['ida_est_revenue'] = revenue_from_ida(spec, ida_series)
        if cap_series is not None and len(cap_series):
            out['capacity_est_revenue'] = revenue_from_capacity(spec, cap_series)
        if act_series is not None and len(act_series):
            out['activation_est_revenue'] = revenue_from_activation(spec, act_series)
        if {'capacity_est_revenue','activation_est_revenue'} <= set(out.keys()):
            out['regelenergie_total'] = out['capacity_est_revenue'] + out['activation_est_revenue']
        return out

