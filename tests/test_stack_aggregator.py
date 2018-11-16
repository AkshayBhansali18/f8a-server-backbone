"""Tests for the stack_aggregator module."""

from unittest import mock

from src import stack_aggregator
import json


def test_extract_component_details():
    """Test the function validate_request_data."""
    with open("tests/data/component_sequence.json", "r") as fin:
        payload = json.load(fin)
    results = stack_aggregator.extract_component_details(payload)
    expected_keys = (
        "ecosystem",
        "name",
        "version",
        "licenses",
        "security",
        "osio_user_count",
        "latest_version",
        "github",
        "code_metrics")
    for expected_key in expected_keys:
        assert expected_key in results, \
            "Can not found the key '{key}' in result data structure".format(key=expected_key)


def test_stack_aggregator_constructor():
    """Test the constructor for the StackAggregator class."""
    obj = stack_aggregator.StackAggregator()
    assert obj


def test_extract_conflict_packages():
    """Test the function _extract_conflict_packages."""
    with open("tests/data/license_component_conflict.json", "r") as f:
        license_payload = json.loads(f.read())

    packages = stack_aggregator._extract_conflict_packages(license_payload)
    assert len(packages) == 1


def mock_dependency_response(*_args, **_kwargs):
    """Mock the call to the insights service."""
    class MockResponse:
        """Mock response object."""

        def __init__(self, json_data, status_code):
            """Create a mock json response."""
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            """Get the mock json response."""
            return self.json_data

    with open('tests/data/dependency_response.json') as f:
        resp = json.loads(f.read())
    return MockResponse(resp, 200)


@mock.patch('requests.get', side_effect=mock_dependency_response)
@mock.patch('requests.Session.post', side_effect=mock_dependency_response)
def test_execute(_mock_get, _mock_post):
    """Test the function execute."""
    with open("tests/data/stack_aggregator_execute_input.json", "r") as f:
        payload = json.loads(f.read())

    s = stack_aggregator.StackAggregator()
    out = s.execute(payload, False)
    assert out['stack_aggregator'] == "success"


def mock_licenses_resp_component_conflict(*_args, **_kwargs):
    """Mock the call to the insights service."""
    class MockResponse:
        """Mock response object."""

        def __init__(self, json_data, status_code):
            """Create a mock json response."""
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            """Get the mock json response."""
            return self.json_data

    with open('tests/data/license_component_conflict.json') as f:
        resp = json.loads(f.read())
    return MockResponse(resp, 200)


@mock.patch('requests.get', side_effect=mock_licenses_resp_component_conflict)
@mock.patch('requests.Session.post', side_effect=mock_licenses_resp_component_conflict)
def test_extract_unknown_packages(_mock_get, _mock_post):
    """Test the function _extract_unknown_packages."""
    with open("tests/data/license_unknown.json", "r") as f:
        license_payload = json.loads(f.read())

    packages = stack_aggregator._extract_unknown_licenses(license_payload)
    assert len(packages) == 2

    with open("tests/data/license_component_conflict.json", "r") as f:
        license_payload = json.loads(f.read())

    packages = stack_aggregator._extract_unknown_licenses(license_payload)
    assert len(packages) == 2


@mock.patch('requests.get', side_effect=mock_licenses_resp_component_conflict)
@mock.patch('requests.Session.post', side_effect=mock_licenses_resp_component_conflict)
def test_extract_license_outliers(_mock_get, _mock_post):
    """Test the function _extract_license_outliers."""
    with open("tests/data/license_component_conflict.json", "r") as f:
        license_payload = json.loads(f.read())

    packages = stack_aggregator._extract_license_outliers(license_payload)
    assert len(packages) == 1


def mock_licenses_resp_unknown(*_args, **_kwargs):
    """Mock the call to the insights service."""
    class MockResponse:
        """Mock response object."""

        def __init__(self, json_data, status_code):
            """Create a mock json response."""
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            """Get the mock json response."""
            return self.json_data

    with open('tests/data/license_unknown.json') as f:
        resp = json.loads(f.read())
    return MockResponse(resp, 200)


@mock.patch('requests.get', side_effect=mock_licenses_resp_unknown)
@mock.patch('requests.Session.post', side_effect=mock_licenses_resp_unknown)
def test_perform_license_analysis(_mock_get, _mock_post):
    """Test the function perform_license_analysis."""
    out, deps = stack_aggregator.perform_license_analysis([], [])
    assert len(deps) == 0


@mock.patch('requests.get', side_effect=mock_dependency_response)
@mock.patch('requests.Session.post', side_effect=mock_dependency_response)
def test_get_dependency_data(_mock_get, _mock_post):
    """Test the function get_dependency_data."""
    resolved = [{
        "package": "io.vertx:vertx-core",
        "version": "3.4.2",
        "deps": [{"package": "io.vertx:vertx-web", "version": "3.4.2"}]
    }]
    out = stack_aggregator.get_dependency_data(resolved, "maven")
    assert len(out['result']) == 1


def test_aggregate_stack_data():
    """Test the function aggregate_stack_data."""
    out = stack_aggregator.aggregate_stack_data({}, "pom.xml", "maven", [], "/home/JohnDoe", False)
    assert out['manifest_name'] == "pom.xml"


if __name__ == '__main__':
    test_extract_component_details()
    test_stack_aggregator_constructor()
    test_extract_conflict_packages()
    test_extract_unknown_packages()
    test_perform_license_analysis()
    test_get_dependency_data()
    test_aggregate_stack_data()
    test_execute()
