import unittest
from src.benchmark_utils import benchmark_model

def dummy_model(x):
    return x * 2

class TestBenchmarkUtils(unittest.TestCase):
    def test_benchmark_model(self):
        avg, times = benchmark_model(dummy_model, 5, runs=3)
        self.assertEqual(len(times), 3)
        self.assertTrue(all(isinstance(t, float) for t in times))
        self.assertTrue(avg > 0)

if __name__ == '__main__':
    unittest.main()
