import unittest
from src.greeter import greet


class TestGreeter(unittest.TestCase):
    def test_t1(self):                       # T1
        self.assertEqual(greet(), "Hello, World!")

    def test_t2(self):                       # T2
        self.assertEqual(greet("Baskaran"), "Hello, Baskaran!")

    def test_t3(self):                       # T3
        self.assertEqual(greet("   "), "Hello, World!")
        self.assertEqual(greet(""), "Hello, World!")

    def test_t4(self):                       # T4
        self.assertEqual(greet("ada", shout=True), "HELLO, ADA!")


if __name__ == "__main__":
    unittest.main()
