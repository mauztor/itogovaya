import unittest
from models import FinancialOperation

class TestFinancialOperation(unittest.TestCase):
    def test_operation_creation(self):
        operation = FinancialOperation(100, "Ремонт", "2023-01-01", "расход")
        self.assertEqual(operation.amount, 100)
        self.assertEqual(operation.category, "Ремонт")
        self.assertEqual(operation.date, "2023-01-01")

if __name__ == "__main__":
    unittest.main()