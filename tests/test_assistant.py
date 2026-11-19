from app.assistant import classify

def test_exam_classification():
    assert classify('When is my DBMS exam?') == 'academics'

def test_event_classification():
    assert classify('Where is the AI workshop?') == 'events'
