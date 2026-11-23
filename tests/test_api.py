"""Model-based tests for HTTP API."""

from hypothesis import strategies as st
from hypothesis import settings
from hypothesis.stateful import RuleBasedStateMachine, rule
from src.client import ApiClient


class ApiStateMachine(RuleBasedStateMachine):
    """State machine for API testing."""

    def __init__(self) -> None:
        """Initialize state machine."""
        super().__init__()
        self.client = ApiClient()

    @rule(uid=st.integers(min_value=1, max_value=100))
    def add_session(self, uid: int) -> None:
        """Test adding a session."""
        status, data = self.client.session_submit(
            uid, {"created": 1700000000}
        )
        assert status == 200
        assert data["uid"] == uid

    @rule()
    def search_sessions(self) -> None:
        """Test searching sessions."""
        status, data = self.client.session_search()
        assert status == 200
        assert isinstance(data, list)

    @rule(uid=st.integers(min_value=1, max_value=100))
    def pop_session(self, uid: int) -> None:
        """Test popping a session."""
        status, _ = self.client.session_pop(uid)
        assert status == 200

    @rule(uid=st.integers(min_value=1, max_value=100))
    def add_instruction(self, uid: int) -> None:
        """Test adding an instruction."""
        status, data = self.client.instruction_submit(
            uid, {"payload": "examples/input_1.txt", "session": 1}
        )
        assert status == 200
        assert data["uid"] == uid

    @rule()
    def search_instructions(self) -> None:
        """Test searching instructions."""
        status, data = self.client.instruction_search(1)
        assert status == 200
        assert isinstance(data, list)

    @rule(instruction_id=st.integers(min_value=1, max_value=100))
    def search_responses(self, instruction_id: int) -> None:
        """Test searching responses."""
        status, data = self.client.response_search(instruction_id)
        assert status == 200
        assert isinstance(data, list)

    @rule()
    def get_report(self) -> None:
        """Test report retrieval."""
        status, data = self.client.report_search()
        assert status == 200
        assert isinstance(data, list)


TestApi = ApiStateMachine.TestCase
TestApi.settings = settings(max_examples=10)
