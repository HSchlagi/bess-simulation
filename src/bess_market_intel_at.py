"""
Österreichische Energiemarkt-Integration für BESS-Simulation
============================================================

Dieses Modul integriert österreichische Energiemarkt-Daten:
- APG Regelenergie (aFRR/FCR/mFRR) Kapazitäts- und Aktivierungspreise
- EPEX Intraday Auktionen (IDA1/IDA2/IDA3)
- ENTSO-E Balancing-Preis-API Integration

Autor: BESS-Simulation Team
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict, List, Callable
import os

def _to_dt(x):
    """Konvertiert zu UTC-Datetime"""
    return pd.to_datetime(x, utc=True, errors='coerce')

def _coerce_float(s: pd.Series) -> pd.Series:
    """Konvertiert String-Spalten zu Float mit Komma-Behandlung"""
    return pd.to_numeric(s.astype(str).str.replace(',', '.', regex=False).str.replace(' ', ''), errors='coerce')

def _normalize_bzn(text: str) -> str:
    """Normalisiert Bidding Zone Namen"""
    return str(text).strip().upper()

@dataclass
class BESSSpec:
    """BESS-Spezifikation für Marktanalysen"""
    power_mw: float
    energy_mwh: float
    availability: float = 0.97
    degradation_factor: float = 0.95

class EpexIDA:
    """EPEX Intraday Auktionen (IDA1/IDA2/IDA3) Parser"""
    
    def load_csv(self, path: str, market_area: Optional[str] = None) -> pd.DataFrame:
        """
        Lädt EPEX IDA CSV-Dateien und normalisiert die Spalten
        
        Args:
            path: Pfad zur CSV-Datei
            market_area: Marktgebiet (Standard: 'AT')
            
        Returns:
            pd.DataFrame: Normalisierte IDA-Daten
        """
        df = pd.read_csv(path)
        cmap = {}
        
        # Automatische Spalten-Zuordnung
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
        
        # Pflicht-Spalten prüfen
        for r in ['start','end','price_eur_mwh']:
            if r not in df.columns:
                raise ValueError(f"Fehlende Spalte '{r}' nach Auto-Mapping. Bitte CSV-Header prüfen.")
        
        # Auktion-Typ automatisch erkennen
        if 'auction' not in df.columns:
            lower = path.lower()
            if 'ida1' in lower: 
                auc = 'IDA1'
            elif 'ida2' in lower: 
                auc = 'IDA2'
            elif 'ida3' in lower: 
                auc = 'IDA3'
            else: 
                auc = 'IDA?'
            df['auction'] = auc
        
        # Marktgebiet setzen
        if 'bzn' not in df.columns:
            df['bzn'] = market_area if market_area else 'AT'
        
        # Daten normalisieren
        df['start'] = _to_dt(df['start'])
        df['end'] = _to_dt(df['end'])
        df['bzn'] = df['bzn'].map(_normalize_bzn)
        df['auction'] = df['auction'].astype(str).str.upper()
        df['price_eur_mwh'] = _coerce_float(df['price_eur_mwh'])
        
        return df[['bzn','auction','start','end','price_eur_mwh']].sort_values(['start','bzn','auction'])

    @staticmethod
    def to_quarter_hour(df: pd.DataFrame) -> pd.DataFrame:
        """
        Konvertiert stündliche Daten zu 15-Minuten-Intervallen
        
        Args:
            df: DataFrame mit stündlichen Daten
            
        Returns:
            pd.DataFrame: 15-Minuten-Intervall-Daten
        """
        rows = []
        for _, r in df.iterrows():
            rng = pd.date_range(r['start'], r['end'], inclusive='left', freq='15T')
            for t0 in rng:
                rows.append({
                    'bzn': r['bzn'], 
                    'auction': r['auction'], 
                    'start': t0,
                    'end': t0 + pd.Timedelta(minutes=15), 
                    'price_eur_mwh': r['price_eur_mwh']
                })
        
        out = pd.DataFrame(rows)
        return out.sort_values(['start','bzn','auction']).reset_index(drop=True)

class APGRegelenergie:
    """APG Regelenergie (aFRR/FCR/mFRR) Parser"""
    
    def load_capacity(self, path: str) -> pd.DataFrame:
        """
        Lädt APG Kapazitätspreise aus CSV
        
        Args:
            path: Pfad zur CSV-Datei
            
        Returns:
            pd.DataFrame: Normalisierte Kapazitätsdaten
        """
        df = pd.read_csv(path)
        cmap = {}
        
        # Automatische Spalten-Zuordnung
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
        
        # End-Zeit setzen falls nicht vorhanden
        if 'end' not in df.columns:
            df['end'] = pd.to_datetime(df['start']) + pd.Timedelta(hours=1)
        else:
            df['end'] = pd.to_datetime(df['end'])
        
        df['start'] = pd.to_datetime(df['start'])
        
        # Produkt-Typ setzen falls nicht vorhanden
        if 'product' not in df.columns:
            df['product'] = 'aFRR_up'
        
        df['product'] = df['product'].astype(str).str.strip().str.replace(' ', '').str.lower()
        df['price_eur_per_mw'] = _coerce_float(df['price_eur_per_mw'])
        
        return df[['start','end','product','price_eur_per_mw']].sort_values('start')

    def load_activation(self, path: str) -> pd.DataFrame:
        """
        Lädt APG Aktivierungspreise aus CSV
        
        Args:
            path: Pfad zur CSV-Datei
            
        Returns:
            pd.DataFrame: Normalisierte Aktivierungsdaten
        """
        df = pd.read_csv(path)
        cmap = {}
        
        # Automatische Spalten-Zuordnung
        for c in df.columns:
            lc = c.lower()
            if 'from' in lc or 'start' in lc or 'beginn' in lc or 'date' in lc:
                cmap[c] = 'start'
            elif 'to' in lc or 'end' in lc or 'ende' in lc:
                cmap[c] = 'end'
            elif 'product' in lc or 'art' in lc:
                cmap[c] = 'product'
            elif 'price' in lc and ('eur/mwh' in lc or '€/mwh' in lc or 'eur per mwh' in lc):
                cmap[c] = 'price_eur_per_mwh'
        
        df = df.rename(columns=cmap)
        
        # End-Zeit setzen falls nicht vorhanden
        if 'end' not in df.columns:
            df['end'] = pd.to_datetime(df['start']) + pd.Timedelta(hours=1)
        else:
            df['end'] = pd.to_datetime(df['end'])
        
        df['start'] = pd.to_datetime(df['start'])
        
        # Produkt-Typ setzen falls nicht vorhanden
        if 'product' not in df.columns:
            df['product'] = 'aFRR_up'
        
        df['product'] = df['product'].astype(str).str.strip().str.replace(' ', '').str.lower()
        df['price_eur_per_mwh'] = _coerce_float(df['price_eur_per_mwh'])
        
        return df[['start','end','product','price_eur_per_mwh']].sort_values('start')

def revenue_from_ida(spec: BESSSpec, ida_series_eur_mwh: pd.Series, 
                    cycles_per_day: float = 0.2) -> float:
    """
    Berechnet Erlöse aus Intraday-Auktionen
    
    Args:
        spec: BESS-Spezifikation
        ida_series_eur_mwh: IDA-Preis-Serie in EUR/MWh
        cycles_per_day: Zyklen pro Tag
        
    Returns:
        float: Jahreserlöse in EUR
    """
    avg_price = ida_series_eur_mwh.mean()
    return spec.power_mw * avg_price * cycles_per_day * 365 * spec.availability * spec.degradation_factor

def revenue_from_capacity(spec: BESSSpec, per_mw_series_eur: pd.Series) -> float:
    """
    Berechnet Erlöse aus Kapazitätsmärkten
    
    Args:
        spec: BESS-Spezifikation
        per_mw_series_eur: Kapazitätspreis-Serie in EUR/MW
        
    Returns:
        float: Jahreserlöse in EUR
    """
    avg_price = per_mw_series_eur.mean()
    return spec.power_mw * avg_price * spec.availability * spec.degradation_factor

def revenue_from_activation(spec: BESSSpec, price_eur_mwh: pd.Series, 
                          assumed_activation_share: float = 0.05) -> float:
    """
    Berechnet Erlöse aus Aktivierungsmärkten
    
    Args:
        spec: BESS-Spezifikation
        price_eur_mwh: Aktivierungspreis-Serie in EUR/MWh
        assumed_activation_share: Angenommener Aktivierungsanteil
        
    Returns:
        float: Jahreserlöse in EUR
    """
    avg_price = price_eur_mwh.mean()
    hours_per_year = 8760
    return spec.power_mw * avg_price * assumed_activation_share * hours_per_year * spec.availability * spec.degradation_factor

class ATMarketIntegrator:
    """Hauptklasse für österreichische Marktintegration"""
    
    def __init__(self, bzn: str = 'AT'):
        """
        Initialisiert den Marktintegrator
        
        Args:
            bzn: Bidding Zone (Standard: 'AT')
        """
        self.bzn = bzn
        self.epex = EpexIDA()
        self.apg = APGRegelenergie()

    def load_ida_csvs(self, paths: List[str]) -> pd.DataFrame:
        """
        Lädt mehrere IDA CSV-Dateien
        
        Args:
            paths: Liste von CSV-Pfaden
            
        Returns:
            pd.DataFrame: Kombinierte IDA-Daten
        """
        dfs = []
        for path in paths:
            if os.path.exists(path):
                df = self.epex.load_csv(path, self.bzn)
                dfs.append(df)
        
        if not dfs:
            raise ValueError(f"Keine gültigen IDA CSV-Dateien gefunden: {paths}")
        
        return pd.concat(dfs, ignore_index=True).sort_values(['start','bzn','auction'])

    def ida_quarter_series(self, df_ida: pd.DataFrame) -> pd.Series:
        """
        Konvertiert IDA-Daten zu 15-Minuten-Preis-Serie
        
        Args:
            df_ida: IDA DataFrame
            
        Returns:
            pd.Series: 15-Minuten-Preis-Serie
        """
        df_q = self.epex.to_quarter_hour(df_ida)
        return df_q.set_index('start')['price_eur_mwh']

    def load_apg_capacity(self, path: str, product_filter: Optional[str] = None) -> pd.Series:
        """
        Lädt APG Kapazitätsdaten
        
        Args:
            path: Pfad zur CSV-Datei
            product_filter: Produkt-Filter (z.B. 'afrr')
            
        Returns:
            pd.Series: Kapazitätspreis-Serie
        """
        df = self.apg.load_capacity(path)
        if product_filter:
            df = df[df['product'].str.contains(product_filter, case=False)]
        return df.set_index('start')['price_eur_per_mw']

    def load_apg_activation(self, path: str, product_filter: Optional[str] = None) -> pd.Series:
        """
        Lädt APG Aktivierungsdaten
        
        Args:
            path: Pfad zur CSV-Datei
            product_filter: Produkt-Filter (z.B. 'afrr')
            
        Returns:
            pd.Series: Aktivierungspreis-Serie
        """
        df = self.apg.load_activation(path)
        if product_filter:
            df = df[df['product'].str.contains(product_filter, case=False)]
        return df.set_index('start')['price_eur_per_mwh']

    def kpis(self, ida_series: Optional[pd.Series] = None,
             cap_series: Optional[pd.Series] = None,
             act_series: Optional[pd.Series] = None,
             spec: Optional[BESSSpec] = None) -> Dict[str, float]:
        """
        Berechnet KPIs für alle verfügbaren Marktdaten
        
        Args:
            ida_series: IDA-Preis-Serie
            cap_series: Kapazitätspreis-Serie
            act_series: Aktivierungspreis-Serie
            spec: BESS-Spezifikation
            
        Returns:
            Dict[str, float]: KPI-Dictionary
        """
        kpis = {}
        
        if ida_series is not None:
            kpis['ida_avg_price_eur_mwh'] = float(ida_series.mean())
            kpis['ida_max_price_eur_mwh'] = float(ida_series.max())
            kpis['ida_min_price_eur_mwh'] = float(ida_series.min())
            kpis['ida_volatility'] = float(ida_series.std())
        
        if cap_series is not None:
            kpis['cap_avg_price_eur_mw'] = float(cap_series.mean())
            kpis['cap_max_price_eur_mw'] = float(cap_series.max())
            kpis['cap_min_price_eur_mw'] = float(cap_series.min())
        
        if act_series is not None:
            kpis['act_avg_price_eur_mwh'] = float(act_series.mean())
            kpis['act_max_price_eur_mwh'] = float(act_series.max())
            kpis['act_min_price_eur_mwh'] = float(act_series.min())
        
        if spec is not None:
            if ida_series is not None:
                kpis['ida_revenue_eur_year'] = revenue_from_ida(spec, ida_series)
            if cap_series is not None:
                kpis['cap_revenue_eur_year'] = revenue_from_capacity(spec, cap_series)
            if act_series is not None:
                kpis['act_revenue_eur_year'] = revenue_from_activation(spec, act_series)
        
        return kpis

