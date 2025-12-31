import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

# Mock firebase_admin to avoid needing real credentials for this basic import/logic test
with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
    with patch("app.app_utils.firestore_store.firebase_admin") as mock_admin:
        with patch("app.app_utils.firestore_store.firestore") as mock_firestore:
            # Mock the client and collection
            mock_client = MagicMock()
            mock_doc_ref = MagicMock()
            mock_doc_ref.id = "test-doc-id"
            mock_client.collection.return_value.add.return_value = (None, mock_doc_ref)
            mock_firestore.client.return_value = mock_client

            from app.app_utils.firestore_store import save_interview_session

            def test_firestore_save():
                print("Testing firestore save logic (mocked)...")

                data = {
                    "topic": "Test Interview",
                    "timestamp": "2025-01-01T10:00:00Z",
                    "userId": "user-123",
                }

                result = save_interview_session(data)
                print(f"Save result: {result}")

                if (
                    result.get("status") == "success"
                    and result.get("id") == "test-doc-id"
                ):
                    print("PASS: Logic works (mocked).")
                else:
                    print(f"FAIL: Unexpected result: {result}")

            if __name__ == "__main__":
                test_firestore_save()
