import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.app_utils.interview_store import save_interview_session, INTERVIEW_FILE


def test_storage():
    print(f"Testing storage to {INTERVIEW_FILE}...")

    # Clean up previous test
    if os.path.exists(INTERVIEW_FILE):
        os.remove(INTERVIEW_FILE)

    data = {
        "topic": "Test Interview",
        "timestamp": "2025-01-01T10:00:00Z",
        "messages": [
            {"role": "user", "text": "Hello"},
            {"role": "agent", "text": "Hi there"},
        ],
    }

    result = save_interview_session(data)
    print(f"Save result: {result}")

    if result.get("status") != "success":
        print("FAIL: Save returned error")
        return

    if not os.path.exists(INTERVIEW_FILE):
        print("FAIL: File not created")
        return

    print("PASS: File created.")

    # Verify content
    import json

    with open(INTERVIEW_FILE) as f:
        content = json.load(f)
        print(f"Content: {content}")
        if len(content) == 1 and content[0]["topic"] == "Test Interview":
            print("PASS: Content verified.")
        else:
            print("FAIL: Content mismatch.")


if __name__ == "__main__":
    test_storage()
