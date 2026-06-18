"""The module under construction (reset to broken)."""


def greet(name=None, shout=False):
    if not name or not name.strip():
        result = "Hello, World!"
    else:
        result = f"Hello, {name.strip()}!"
    if shout:
        result = result.upper()
    return result
