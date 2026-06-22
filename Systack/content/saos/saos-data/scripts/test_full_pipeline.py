#!/usr/bin/env python3
"""
SAOS Complete Pipeline Test
Tests all provisioning components end-to-end.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json

sys.path.insert(0, os.path.dirname(__file__))

from provision_vps import generate_cloud_init, TIER_PLANS
from deploy_templates import REQUIRED_WORKFLOWS


class TestCloudInitGeneration(unittest.TestCase):
    """Test cloud-init templates."""
    
    def test_all_tiers(self):
        """Cloud-init generates for all tiers."""
        for tier in TIER_PLANS.keys():
            ci = generate_cloud_init("123", tier, "TestAgent", "tskey-test")
            self.assertIn("#cloud-config", ci)
            self.assertIn(f"saos-123", ci)

    def test_tailscale_config(self):
        """Cloud-init includes Tailscale setup."""
        ci = generate_cloud_init("456", "business", "Agent", "tskey-auth")
        self.assertIn("tailscale up", ci)
        self.assertIn("tskey-auth", ci)
        self.assertIn("tag:saos-client", ci)

    def test_ollama_config(self):
        """Cloud-init includes Ollama setup."""
        ci = generate_cloud_init("789", "business", "Agent", "tskey-test")
        self.assertIn("ollama pull", ci)
        self.assertIn("qwen2.5:7b", ci)


class TestTierConfigurations(unittest.TestCase):
    """Test tier plan mappings."""
    
    def test_business_tier(self):
        """Business tier has correct plan."""
        self.assertEqual(TIER_PLANS["business"]["plan"], "vhp-4c-16gb")
        self.assertEqual(TIER_PLANS["business"]["region"], "ord")
    
    def test_enterprise_tier(self):
        """Enterprise tier has correct plan."""
        self.assertEqual(TIER_PLANS["enterprise"]["plan"], "vhp-4c-16gb")
    
    def test_test_tier(self):
        """Test tier is cheaper."""
        self.assertEqual(TIER_PLANS["test"]["plan"], "vc2-1c-1gb")


class TestTemplateRequirements(unittest.TestCase):
    """Test template requirements per tier."""
    
    def test_business_workflows(self):
        """Business tier has correct workflows."""
        self.assertIn("booking-system.json", REQUIRED_WORKFLOWS["business"])
        self.assertIn("invoice-pipeline.json", REQUIRED_WORKFLOWS["business"])
    
    def test_enterprise_has_more(self):
        """Enterprise has more workflows than business."""
        self.assertGreater(len(REQUIRED_WORKFLOWS["enterprise"]), 
                          len(REQUIRED_WORKFLOWS["business"]))


class TestEmailGeneration(unittest.TestCase):
    """Test email template generation."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_welcome_email_html(self):
        """Welcome email generates valid HTML."""
        from send_client_email import generate_welcome_email
        
        client_data = {
            "client_id": "TEST",
            "client_name": "Test Business",
            "contact_name": "Test",
            "agent_name": "Testy",
            "tier": "business",
            "vps_ip": "192.0.2.1",
            "tailscale_url": "https://test.tailnet.ts.net"
        }
        
        html = generate_welcome_email(client_data)
        self.assertIn("SAOS Fleet is Live", html)
        self.assertIn("Test Business", html)
        self.assertIn("Testy", html)
        self.assertIn("https://test.tailnet.ts.net", html)


def run_tests():
    """Run all tests."""
    print("🧪 Running SAOS Pipeline Tests...\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestCloudInitGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestTierConfigurations))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplateRequirements))
    suite.addTests(loader.loadTestsFromTestCase(TestEmailGeneration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All pipeline tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
