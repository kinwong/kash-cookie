import unittest
import tensorflow as tf

from core import broker

def test_constant():
    """ Test a tesorflow session """
    sess = tf.Session()
    first = tf.constant(4)
    second = tf.constant(5)
    return sess.run(first * second)

class TensorFlowTest(unittest.TestCase):
    def test_constent(self):
        result = test_constant()
        print(result)
        self.assertEqual(20, result)

if __name__ == '__main__':
    unittest.main()
