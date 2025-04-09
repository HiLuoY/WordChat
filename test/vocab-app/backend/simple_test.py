import unittest

class SimpleTest(unittest.TestCase):
    def test_simple(self):
        print("这是一个简单的测试")
        self.assertTrue(True)

if __name__ == '__main__':
    print("开始运行简单测试...")
    unittest.main() 