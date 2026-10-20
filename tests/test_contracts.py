import sys, unittest, sqlite3, json
from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from common import load_clean

class DataContractTests(unittest.TestCase):
    def test_conflicting_duplicates_rejected(self):
        with self.assertRaises(ValueError): load_clean(pd.DataFrame({'id':[1,1],'value':[2,3]}),['id'])
    def test_exact_retry_removed(self):
        clean,n=load_clean(pd.DataFrame({'id':[1,1],'value':[2,2]}),['id'])
        self.assertEqual((len(clean),n),(1,1))
    def test_null_key_rejected(self):
        with self.assertRaises(AssertionError):load_clean(pd.DataFrame({'id':[None]}),['id'])
    def test_bridge(self):
        d=pd.read_csv(ROOT/'data/processed/monthly_metrics.csv')
        np.testing.assert_allclose(d.end_mrr,d[['start_mrr','new_mrr','reactivation_mrr','expansion_mrr','contraction_mrr','churn_mrr']].sum(axis=1),atol=1e-7)
    def test_nrr_excludes_acquisition(self):
        d=pd.read_csv(ROOT/'data/processed/fact_subscription.csv')
        self.assertEqual(float(d.loc[d.previous_mrr==0,'retained_mrr'].sum()),0)
    def test_sql_python_parity(self):
        a=pd.read_csv(ROOT/'reports/sql_result.csv');b=pd.read_csv(ROOT/'data/processed/monthly_metrics.csv')
        np.testing.assert_allclose(a.end_mrr,b.end_mrr)
        np.testing.assert_allclose(a.nrr,b.nrr,equal_nan=True)
    def test_relationships_and_grain(self):
        d=pd.read_csv(ROOT/'data/processed/fact_subscription.csv');a=pd.read_csv(ROOT/'data/processed/dim_account.csv')
        self.assertFalse(d.duplicated(['account_id','month']).any());self.assertTrue(set(d.account_id)<=set(a.account_id))
        self.assertTrue((d.mrr>=0).all())
