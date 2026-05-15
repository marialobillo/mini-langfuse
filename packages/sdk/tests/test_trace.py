from mini_langfuse_sdk import trace


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

def test_trace_preserves_function_name():
    def my_function():
        return 42
    
    traced = trace(my_function)
    assert traced.__name__ == "my_function"