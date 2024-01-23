from circuitbreaker import circuit
import time

def failureHandler():
    return "Handled failure using circuit breaker"

@circuit(failure_threshold=2, recovery_timeout=5, fallback_function=failureHandler)
def my_operation():
    raise Exception("Oops! Something went wrong.")

for _ in range(4):
    try:
        result = my_operation()
        print("Result:", result)
    except Exception as e:
        print("Caught an exception:", e)


time.sleep(5)

print("After 5 seconds")

try:
    result = my_operation()
    print("Result:", result)
except Exception as e:
    print("Caught an exception:", e)