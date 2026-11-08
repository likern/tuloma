"""Compare the NumPy query with exact rational, clipped-edge geometry."""
from fractions import Fraction as F
from pathlib import Path
import json
import random
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
JOURNAL = Path(__file__).resolve().parents[3] / "apps/journal"
from tuloma_reference.los import X, Z, profile_los, compare_profile_los, line_height, linear_blend, _below_intervals


def edge_oracle(xa, xb, ha, hb, heights):
    """Independent edge clipping and exact orientation, including contact."""
    xs=list(map(F, map(int, X)))
    zs=list(map(F, heights))
    xa,xb,ha,hb=map(F,(xa,xb,ha,hb))
    if xa==xb: return "same"
    def ground(x):
        for i in range(len(xs)-1):
            if xs[i]<=x<=xs[i+1]:
                return zs[i]+(zs[i+1]-zs[i])*(x-xs[i])/(xs[i+1]-xs[i])
        raise AssertionError("outside oracle domain")
    za,zb=ground(xa)+ha,ground(xb)+hb
    left,right=sorted((xa,xb))
    zl,zr=(za,zb) if xa<xb else (zb,za)
    contact=False
    for i in range(len(xs)-1):
        a,b=max(left,xs[i]),min(right,xs[i+1])
        if a>=b: continue
        for x in (a,(a+b)/2,b):
            orientation=(right-left)*(ground(x)-zl)-(zr-zl)*(x-left)
            if orientation>0: return "blocked"
            if orientation==0 and left<x<right: contact=True
    return "touch" if contact else "visible"


class LOSGeometryTests(unittest.TestCase):
    def test_control_scenarios_and_roots(self):
        self.assertEqual(profile_los(0,80)["kind"],"blocked")
        self.assertEqual(profile_los(0,80,0,12)["kind"],"touch")
        self.assertEqual(profile_los(0,80,0,16)["kind"],"visible")
        r=profile_los(0,80,diagnostics=True)
        np.testing.assert_allclose(r["below"],[[float(F(106,3)),float(F(298,7))]])
        np.testing.assert_allclose(r["below_segments"],[[float(F(106,3)),6,float(F(298,7)),6]])
        self.assertEqual(len(r["diagnostics"]["nodes"]),8)
        peak=r["diagnostics"]["nodes"][3]
        self.assertEqual((peak["x"],peak["t"],peak["line_z"],peak["gap"]),(40,.5,6,6))

    def test_same_surface_intersections_different_answers(self):
        for height,expected in [(3,"blocked"),(-3,"visible"),(0,"touch")]:
            z=np.zeros_like(Z);z[1]=height
            self.assertEqual(profile_los(0,23,z=z)["kind"],expected)

    def test_hidden_intervals_keep_isolated_contact_separate(self):
        self.assertEqual(_below_intervals([0,1,2,3,4],[-1,1,0,1,-1]),[[.5,2],[2,3.5]])
        self.assertEqual(_below_intervals([0,1,2,3],[-1,1,1,-1]),[[.5,2.5]])

    def test_empty_interval_and_vertical_case(self):
        self.assertEqual(profile_los(12,20)["kind"],"touch")
        self.assertEqual(profile_los(12,20,0,1)["kind"],"visible")
        r=profile_los(40,40,1,2,diagnostics=True)
        self.assertEqual(r["kind"],"same")
        self.assertEqual(r["diagnostics"]["nodes"],[])

    def test_reversal(self):
        for a,b,ha,hb in [(0,80,0,0),(3.5,91,2,5),(12,20,0,1)]:
            r=profile_los(a,b,ha,hb,diagnostics=True)
            s=profile_los(b,a,hb,ha,diagnostics=True)
            self.assertEqual(r["kind"],s["kind"])
            np.testing.assert_allclose(r["below"],s["below"])
            np.testing.assert_allclose(r["diagnostics"]["difference"],s["diagnostics"]["difference"])

    def test_diagnostics_do_not_change_query(self):
        r=profile_los(0,80)
        d=profile_los(0,80,diagnostics=True)
        d.pop("diagnostics")
        self.assertEqual(r,d)
        self.assertNotIn("diagnostics",r)

    def test_exact_edge_oracle(self):
        rng=random.Random(20261104)
        for _ in range(300):
            heights=[F(rng.randrange(-10,41),2) for _ in X]
            xa,xb=F(rng.randrange(201),2),F(rng.randrange(201),2)
            ha,hb=F(rng.randrange(9),2),F(rng.randrange(9),2)
            expected=edge_oracle(xa,xb,ha,hb,heights)
            actual=profile_los(float(xa),float(xb),float(ha),float(hb),z=list(map(float,heights)))
            self.assertEqual(actual["kind"],expected,(xa,xb,ha,hb,heights))

    def test_sampling_is_not_vertex_checking(self):
        r=compare_profile_los(0,80,step=25,diagnostics=True)
        self.assertEqual((r["exact"]["kind"],r["sampled"]),("blocked","visible"))
        np.testing.assert_allclose(r["samples"],[[25,.6],[50,2.2],[75,27/7]])
        self.assertEqual(compare_profile_los(0,80,step=20)["sampled"],"blocked")
        self.assertEqual(compare_profile_los(12,20,step=25)["sampled"],"empty")

    def test_numerical_policy(self):
        z=np.zeros_like(Z);z[1]=5e-10
        self.assertEqual(profile_los(0,23,z=z)["kind"],"touch")
        self.assertEqual(profile_los(0,23,z=z,atol=0)["kind"],"blocked")
        for atol in (-1,np.nan,np.inf):
            with self.assertRaises(ValueError): profile_los(0,80,atol=atol)

    def test_invalid_data(self):
        for args in [(-1,80,0,0),(0,101,0,0),(0,80,-1,0),(0,80,0,np.inf)]:
            with self.assertRaises(ValueError): profile_los(*args)
        for z in ([1,2],np.full_like(Z,np.nan)):
            with self.assertRaises(ValueError): profile_los(0,80,z=z)

    def test_teaching_data_and_shared_interpolation(self):
        np.testing.assert_allclose(line_height([10,20,30],10,4,30,12),[4,8,12])
        np.testing.assert_allclose(linear_blend(-3,-1,[0,.5,1]),[-3,-2,-1])
        with self.assertRaises(ValueError): line_height(10,10,4,10,12)
        data=json.loads((JOURNAL/"assets/lesson-data.json").read_text())
        self.assertEqual(data["worked"]["result"],profile_los(0,80,diagnostics=True))
        self.assertEqual(data["interpolation"][50],{"t":.5,"x":20.,"z":8.})
        self.assertEqual(data["proofs"][0]["points"][50]["value"],-2.)


if __name__=="__main__": unittest.main()
