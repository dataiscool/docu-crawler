import unittest

class TestBasic(unittest.TestCase):
    def test_import(self):
        """Test that the package can be imported"""
        import src
        self.assertTrue(True, "Package imported successfully")

if __name__ == "__main__":
    unittest.main()