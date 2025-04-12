# pylint: disable=r0903,w0612,w0621
import datetime
import pytest
import main as ml_client


# DummyCollection simulates MongoDB collection operations
class DummyCollection:
    def __init__(self):
        self.data = []

    def find(self, query):
        return [doc for doc in self.data if "input_text" in doc and "translated_text" not in doc]

    def update_one(self, query, update):
        for doc in self.data:
            if doc.get("_id") == query.get("_id"):
                for key, value in update.get("$set", {}).items():
                    doc[key] = value
                return

# DummyTranslator now creates an instance with a properly set text attribute.
class DummyTranslation:
    def __init__(self, text):
        self.text = f"translated_{text}"

class DummyTranslator:
    def translate(self, text, dest):
        return DummyTranslation(text)

# Pytest fixture to set up the ML client globals.
@pytest.fixture
def ml_client_setup(monkeypatch):
    dummy_sensor_data = DummyCollection()
    dummy_sensor_data.data = [
        {"_id": 1, "input_text": "hello", "target_language": "fr"},
        {"_id": 2, "input_text": "world",
          "target_language": "es", "translated_text": "old_translation"},
        {"_id": 3, "input_text": "test", "target_language": "de"}
    ]
    dummy_translator = DummyTranslator()
    monkeypatch.setattr(ml_client, "db", type("DummyDB", (), {"sensor_data": dummy_sensor_data})())
    monkeypatch.setattr(ml_client, "translator", dummy_translator)

    return ml_client

# Tests

def test_process_untranslated_records_updates_pending(ml_client_setup, capsys):
    """
    Verify that process_untranslated_records() correctly updates documents
    that do not have 'translated_text'.
    """
    ml_client_setup.process_untranslated_records()

    dummy_data = ml_client_setup.db.sensor_data.data

    record1 = next((doc for doc in dummy_data if doc["_id"] == 1), None)
    record3 = next((doc for doc in dummy_data if doc["_id"] == 3), None)
    record2 = next((doc for doc in dummy_data if doc["_id"] == 2), None)

    assert record1 is not None
    assert "translated_text" in record1
    assert record1["translated_text"] == "translated_hello"

    assert record3 is not None
    assert "translated_text" in record3
    assert record3["translated_text"] == "translated_test"
    assert record2["translated_text"] == "old_translation"

def test_process_untranslated_records_no_pending(ml_client_setup, capsys):
    """
    Verify that if no document is pending (i.e. all documents have a 'translated_text'),
    the process prints an appropriate message.
    """
    for doc in ml_client_setup.db.sensor_data.data:
        doc["translated_text"] = "existing_translation"

    ml_client_setup.process_untranslated_records()

    captured = capsys.readouterr().out
    assert "No new translation jobs found." in captured
