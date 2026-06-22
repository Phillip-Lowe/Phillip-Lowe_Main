#!/usr/bin/env python3
"""
SAOS Provisioning Test Suite
Tests VPS provisioning without creating real instances.
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from provision_vps import VultrProvisioner, generate_cloud_init, TIER_PLANS


class TestCloudInit(unittest.TestCase):
    """Test cloud-init generation."""
    
    def test_generate_cloud_init(self):
        """Cloud-init contains required components."""
        ci = generate_cloud_init("123", "business", "Percy", "tskey-auth-test")
        
        self.assertIn("#cloud-config", ci)
        self.assertIn("tailscale up", ci)
        self.assertIn("saos-123", ci)
        self.assertIn("qwen2.5:7b", ci)
        self.assertIn("docker.io", ci)
        self.assertIn("ufw", ci)
        self.assertIn("fail2ban", ci)
        self.assertIn("ollama", ci)
    
    def test_cloud_init_base64(self):
        """Cloud-init can be base64 encoded."""
        import base64
        ci = generate_cloud_init("456", "enterprise", "Alex", "tskey-auth-test")
        encoded = base64.b64encode(ci.encode()).decode()
        decoded = base64.b64decode(encoded).decode()
        self.assertEqual(ci, decoded)
    
    def test_all_tiers_have_configs(self):
        """All defined tiers have required fields."""
        for tier_name, config in TIER_PLANS.items():
            self.assertIn("plan", config)
            self.assertIn("region", config)
            self.assertIn("os_id", config)
            self.assertIn("description", config)


class TestVultrProvisioner(unittest.TestCase):
    """Test VultrProvisioner class."""
    
    @patch.dict(os.environ, {"VULTR_API_KEY": "test-key-123"})
    def test_init_with_env(self):
        """Provisioner reads API key from environment."""
        p = VultrProvisioner()
        self.assertEqual(p.api_key, "test-key-123")
    
    def test_init_without_key(self):
        """Provisioner fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                VultrProvisioner()
    
    @patch.dict(os.environ, {"VULTR_API_KEY": "test-key"})
    @patch("provision_vps.requests.request")
    def test_list_instances(self, mock_request):
        """List instances parses response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "instances": [
                {"id": "inst-1", "label": "saos-test-1", "status": "active"},
                {"id": "inst-2", "label": "saos-test-2", "status": "pending"}
            ]
        }
        mock_response.text = json.dumps(mock_response.json.return_value)
        mock_request.return_value = mock_response
        
        p = VultrProvisioner()
        instances = p.list_instances()
        
        self.assertEqual(len(instances), 2)
        self.assertEqual(instances[0]["label"], "saos-test-1")
    
    @patch.dict(os.environ, {"VULTR_API_KEY": "test-key"})
    @patch("provision_vps.requests.request")
    def test_create_instance(self, mock_request):
        """Create instance returns instance data."""
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.json.return_value = {
            "instance": {
                "id": "new-inst-123",
                "label": "saos-999",
                "status": "pending",
                "date_created": "2026-06-17T00:00:00Z"
            }
        }
        mock_response.text = json.dumps(mock_response.json.return_value)
        mock_request.return_value = mock_response
        
        p = VultrProvisioner()
        instance = p.create_instance("999", "test", "Testy", "tskey-auth-test")
        
        self.assertEqual(instance["id"], "new-inst-123")
        self.assertEqual(instance["label"], "saos-999")
        
        # Verify request payload
        call_args = mock_request.call_args
        payload = call_args.kwargs.get("json", {})
        self.assertEqual(payload["label"], "saos-999")
        self.assertEqual(payload["plan"], "vc2-1c-1gb")  # test tier plan
        self.assertIn("user_data", payload)


def run_tests():
    """Run all tests."""
    print("🧪 Running SAOS Provisioning Tests...\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestCloudInit))
    suite.addTests(loader.loadTestsFromTestCase(TestVultrProvisioner))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
