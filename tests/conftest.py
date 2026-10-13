import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-live-llm",
        action="store_true",
        default=False,
        help="Run tests that make live LLM API calls.",
    )


@pytest.fixture
def run_live_llm(request):

    return request.config.getoption(
        "--run-live-llm"
    )