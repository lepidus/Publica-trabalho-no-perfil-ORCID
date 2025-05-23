import unittest
from unittest.mock import patch, Mock
from orcid.orcid_client import OrcidClient

class TestOrcidClient(unittest.TestCase):

    def setUp(self):
        self.client = OrcidClient("fake_client_id", "fake_client_secret", "http://localhost/redirectUrlExample")
    
    @patch('orcid.orcid_client.requests.post')
    def test_get_orcid_id_and_access_token_with_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "fake_token",
            "orcid": "0000-0000-0000-0000",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        token_info = self.client.get_orcid_id_and_access_token("mock_auth_code")

        self.assertEqual(token_info["access_token"], "fake_token")
        self.assertEqual(token_info["orcid"], "0000-0000-0000-0000")
        self.assertEqual(token_info["expires_in"], 3600)
    
    @patch('orcid.orcid_client.requests.post')
    def test_publish_work_with_success(self, mock_post):
        mock_response = Mock()
        mock_response.headers = {"location": "https://sandbox.orcid.org/0000-0000-0000-0000/work/12345"}
        mock_response.status_code = 201
        mock_response.json.return_value = {"message": "Work added", "put-code": "12345"}
        mock_post.return_value = mock_response

        data = {"title": "My article"}
        status, response = self.client.publish_to_orcid("fake_token", "0000-0000-0000-0000", data)

        self.assertEqual(status, 201)
        self.assertIn("Work added", response["message"])
        self.assertIn("12345", response["put-code"])
    
    @patch('orcid.orcid_client.requests.post')
    def test_error_when_publish_to_orcid(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Permission denied"
        mock_post.return_value = mock_response

        data = {"title": "My article"}
        status, response = self.client.publish_to_orcid("invalid_token", "0000-0000-0000-0000", data)
        
        self.assertEqual(status, 403)
        self.assertIn("Permission denied", response["error"])
    
    def test_validate_access_token_permission_with_expired_token(self):
        expires_in = 3600
        is_valid_token = self.client.is_authorized_access_token(expires_in)
            
        self.assertFalse(is_valid_token)

    def test_oauth_url_build_with_success(self):
        expected_suffix_link = "oauth/authorize?client_id=fake_client_id&response_type=code&scope=None&redirect_uri=http://localhost/redirectUrlExample"
        self.assertIn(expected_suffix_link, self.client.get_auth_url())
    
if __name__ == "__main__":
    unittest.main()