import server, unittest

class IntegrationTestCase(unittest.TestCase):
    def test_home(self):
        test_client = server.app.test_client()
        result = test_client.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn('<h3>Plan your travel. Together.</h3>', result.data)

    def test_login(self):
    	test_client = server.app.test_client()
    	result = test_client.get('/login')
    	print result
    	self.assertIn('Login', result.data)




if __name__ == "__main__":    
    unittest.main()