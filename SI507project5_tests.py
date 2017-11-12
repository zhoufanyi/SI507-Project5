import unittest
from datetime import datetime
from SI507project5_code import *

class tumblr_test_case(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now().strftime(DATETIME_FORMAT)
        self.url = 'https://www.google.com'
        self.params_diction = {'A':'Ann Arbor','B':'Michigan'}
        self.identifier = 'TUMBLR'
        self.request_url = 'https://api.tumblr.com/v2/blog/'+'test.com/posts'
    
    def tearDown(self):
        pass
    
    def test_has_expired(self):
        self.assertFalse(has_expired(self.now, expire_in_days = 7))
    
    def test_create_request_identifier(self):
        right_str = 'https://www.google.com?A_Ann Arbor_B_Michigan'.upper()
        self.assertEqual(create_request_identifier(self.url,self.params_diction),right_str)

    def test_get_from_cache(self):
        self.assertEqual(len(get_from_cache(self.identifier,CREDS_DICTION)),5)
        self.assertEqual(get_from_cache(self.identifier,CREDS_DICTION)[0], CLIENT_KEY)
        self.assertEqual(get_from_cache(self.identifier,CREDS_DICTION)[1], CLIENT_SECRET)

    def test_get_data_from_api(self):
        self.assertIsInstance(get_data_from_api(self.request_url,'TUMBLR',self.params_diction),dict)

    def test_get_tokens_from_service(self):
        self.assertEqual(len(get_tokens_from_service(self.identifier)),5)
        self.assertEqual(get_tokens_from_service(self.identifier)[0], CLIENT_KEY)
        self.assertEqual(get_tokens_from_service(self.identifier)[1], CLIENT_SECRET)













if __name__ == "__main__":
    unittest.main(verbosity=2)
