from mini_langfuse_sdk import trace


def test_decorated_function_returns_same_value():

    original_func = lambda: 12
    traced_func = trace(original_func)
    
    assert traced_func() == original_func()
