"""Tests for the plan checker. These do not test physical hardware."""
import copy
import tempfile
import unittest
from pathlib import Path
from check_plan import load_json, validate, inspect_repo

ROOT=Path(__file__).resolve().parents[1]
class PlanChecks(unittest.TestCase):
    def setUp(self):
        self.a=load_json(ROOT/'contracts/architecture.json')
        self.m=load_json(ROOT/'contracts/axis_allocation.json')
        self.t=load_json(ROOT/'contracts/acceptance_targets.json')
    def good(self):
        return validate(self.a,self.m,self.t)['passed']
    def test_baseline(self):
        self.assertTrue(self.good())
    def test_duplicate_axis(self):
        self.m['axis_order'][1]=self.m['axis_order'][0]
        self.assertFalse(self.good())
    def test_wrong_order(self):
        self.m['axes'][0],self.m['axes'][1]=self.m['axes'][1],self.m['axes'][0]
        self.assertFalse(self.good())
    def test_port_collision(self):
        self.m['axes'][1]['logical_port']=self.m['axes'][0]['logical_port']
        self.assertFalse(self.good())
    def test_missing_region_index(self):
        self.m['regions'][0]['sensor_indices'].pop()
        self.assertFalse(self.good())
    def test_false_hardware_pass(self):
        self.t['metrics'][0]['status']='passed'
        self.assertFalse(self.good())
    def test_premature_release(self):
        self.a['release_gates']['pcb_manufacturing_released']=True
        self.assertFalse(self.good())
    def test_wrong_can_format(self):
        self.a['electronics_baseline']['can_format']='CAN_FD'
        self.assertFalse(self.good())
    def test_overloaded_bus(self):
        self.a['timing_targets']['acquisition_hz']=1000
        self.assertFalse(self.good())
    def test_missing_checkout(self):
        with tempfile.TemporaryDirectory() as d:
            result=inspect_repo(Path(d),self.a,self.m)
            self.assertFalse(result['compatible_axis_order'])
            self.assertTrue(result['read_only'])

if __name__=='__main__':
    unittest.main(verbosity=2)
