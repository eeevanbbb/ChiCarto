import os
import main
import unittest
import tempfile

class ChiCartoTestCase(unittest.TestCase):

    def setUp(self):
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()
        main.init_db()

    def tearDown(self):
        main.app.config['TESTING'] = False

if __name__ == '__main__':
    unittest.main()
