import pytest
from mini_langfuse_sdk import trace
from mini_langfuse_sdk.tracer import default_tracer

@pytest.fixture(autouse=True)
def clean_tracer():
    default_tracer.records.clear()
    yield


def test_decorated_function_returns_same_value():
    original_func = lambda: 12
    traced_func = trace(original_func)
    assert traced_func() == 12

def test_decorated_function_works_with_positional_arguments():
    original_func = lambda a, b: a * b 
    traced_func = trace(original_func)
    assert traced_func(2,3) == 6

def test_decorated_function_works_with_keyword_arguments():
    original_func = lambda a, b: a * b
    traced_func = trace(original_func)
    assert traced_func(a=2,b=3) == 6

def test_trace_preserves_function_metadata():
    def my_function():
        return 42
    
    traced = trace(my_function)
    assert traced.__name__ == "my_function"

def test_tracer_captures_function_name():
    @trace
    def my_function():
        return 42
    
    my_function()

    assert default_tracer.records[-1]["name"] == "my_function"

def test_trace_captures_positional_input():
    @trace
    def add(a, b):
        return a + b
    
    add(2, 3)
    assert default_tracer.records[-1]["input"] == {"args": [2, 3], "kwargs": {}}

def test_trace_captures_output():
    @trace
    def add(a, b):
        return a + b
    
    add(2, 3)
    assert default_tracer.records[-1]["output"] == 5