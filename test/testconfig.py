from unittest.mock import MagicMock
from src.config import Config

class TestConfig:
  def test_verify_valid_app(self):
    config = Config()
    config.credentials = MagicMock(return_value={
      "github_app_id": "12345",
      "github_app_installation_id": "67890",
      "github_app_private_key": "-----BEGIN RSA PRIVATE KEY-----",
      "github_org": "test-org"
    })

    errors, is_valid = config.verify()
    print(errors)
    assert is_valid is True
    assert len(errors) == 0

  def test_verify_valid_pat(self):
    config = Config()
    config.credentials = MagicMock(return_value={
      "github_token": "ghp_abcdefghijklmnopqrst",
      "github_org": "test-org"
    })

    errors, is_valid = config.verify()
    assert is_valid is True
    assert len(errors) == 0

  def test_verify_missing_app_id(self):
    config = Config()
    config.credentials = MagicMock(return_value={
      "github_app_installation_id": "67890",
      "github_app_private_key": "some-private-key",
      "github_org": "test-org"
    })

    errors, is_valid = config.verify()

    assert is_valid is False
    assert "GitHub App ID is missing" in errors

  def test_verify_missing_installation_id(self):
    config = Config()
    config.credentials = MagicMock(return_value={
      "github_app_id": "12345",
      "github_app_private_key": "some-private-key",
      "github_org": "test-org"
    })

    errors, is_valid = config.verify()

    assert is_valid is False
    assert "GitHub App Installation ID is missing" in errors

  def test_verify_invalid_private_key(self):
    config = Config()
    config.credentials = MagicMock(return_value={
      "github_app_id": "12345",
      "github_app_installation_id": "67890",
      "github_app_private_key": "invalid_private_key",
      "github_org": "test-org"
    })

    errors, is_valid = config.verify()

    assert is_valid is False
    assert "GitHub App Private Key is invalid (must be a valid RSA private key)" in errors

  def test_verify_invalid_pat(self):
    config = Config()
    config.credentials = MagicMock(return_value={
      "github_token": "invalid_token",
      "github_org": "test-org"
    })

    errors, is_valid = config.verify()

    assert is_valid is False
    assert "GitHub token appears to be invalid (should start with 'ghp_' or 'github_pat_')" in errors

  def test_verify_both_configured(self):
    config = Config()
    config.credentials = MagicMock(return_value={
      "github_app_id": "12345",
      "github_app_installation_id": "67890",
      "github_app_private_key": "some-private-key",
      "github_token": "ghp_abcdefghijklmnopqrst",
      "github_org": "test-org"
    })

    errors, is_valid = config.verify()
    assert is_valid is True

  def test_verify_none_configured(self):
    config = Config()
    config.credentials = MagicMock(return_value={
      "github_org": "test-org"
    })

    errors, is_valid = config.verify()

    assert is_valid is False
    assert "No GitHub authentication configured. Please provide either GitHub App credentials or a Personal Access Token." in errors

  def test_verify_missing_org(self):
    config = Config()
    config.credentials = MagicMock(return_value={
      "github_token": "ghp_abcdefghijklmnopqrst"
    })

    errors, is_valid = config.verify()

    assert is_valid is False
    assert "GitHub organization is not specified" in errors
