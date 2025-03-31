import sys
import time
from functools import wraps

def throttle_requests():
    """
    Decorator to throttle requests based on token usage.

    Returns:
        function: Wrapped function with throttling.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            result = func(self, *args, **kwargs)
            elapsed_time = time.time() - start_time
            if self.token_counter.total_llm_token_count >= self.model_tpm:
                sleep_time = 60 - elapsed_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.token_counter.reset_counts()
            return result

        return wrapper

    return decorator


def throttle_cross_query_requests(func):
    """
    Decorator to throttle cross-query requests.
    To be used in app.scripts.Demo.Demo.run() if you run into an issue with the API's rate limiters.

    Args:
        func (function): Function to wrap.

    Returns:
        function: Wrapped function with throttling.
    """

    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        elapsed_time = time.time() - start_time
        remainder = elapsed_time % 60
        sleep_time = 60 - remainder
        if sleep_time > 0:
            for remaining in range(int(sleep_time), 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write(f"Waiting for {remaining} seconds...")
                sys.stdout.flush()
                time.sleep(1)
        return result

    return wrapper
