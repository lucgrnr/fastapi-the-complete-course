from fastapi.testclient import TestClient
from ..main import app
from fastapi import status
# The .. in the import statement from ..main import app is used to indicate that main.py is located in the parent directory of the test directory. 
# This is a common pattern in Python when organizing project structures, especially in applications that have a clear separation between the application code and the test code.
# Add a comment here: what

client = TestClient(app)


def test_return_health_check():
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'Healthy'}

"""
WHY AUTOMATED TESTING MATTERS (VS. MANUAL TESTING):

Manual testing only feels faster when initially building an endpoint,
taking seconds to click around in Swagger or Postman. However, it scales
poorly: re-testing every endpoint, auth flow, and database state after a
refactor quickly wastes hours and invites human error.

Automated tests provide immense long-term protection by asserting true
database side-effects rather than just HTTP status codes. A route might
return 204 No Content, but without tests checking the database directly,
a missing commit or silent exception could leave orphaned or undeleted
records unnoticed until production.

They enable fearless refactoring and immediate regression detection.
When upgrading libraries (e.g., SQLAlchemy 2.0 or Pydantic v2) or adding
new fields, a single 1-second `pytest` run flags broken routes instantly.
They also serve as mandatory safety gates in CI/CD pipelines to block
broken commits before deployment.

To reduce boilerplate and avoid test fatigue, keep your suite focused on
core contracts: the happy paths (mutations and reads), boundary guards
(401/404 handling), and true database persistence. Use tools like
`@pytest.mark.parametrize` to test multiple edge cases in one concise block.
"""