# Issues found by static analysis

Line numbers refer to the **original** `delivery_system.py` (before any fixes).
Sorted with the most severe first. Tool codes: B = Bandit, W/C/R = Pylint, E = Flake8.
Rows marked "manual" were found by reading and running the program, not by a tool.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Unsafe pickle deserialization (B301, Medium) | Security | 49 | `pickle.load` can run arbitrary code if `orders.pkl` is tampered with. | Replaced pickle with `json` for backup and restore. Restore converts the string keys back to `int` and resets `next_id` so new orders do not overwrite old ones. |
| Pickle module imported (B403, Low) | Security | 2 | Same root cause as above: importing `pickle` is flagged as risky. | Removed `import pickle`; JSON is used instead. |
| Silent `try/except/pass` (B110 Low, W0702, E722) | Bug / Security | 22-25 | A bare `except:` hides every error. A bad order id or any other failure disappears silently. | Check explicitly: reject statuses not in `VALID_STATUSES` and unknown order ids, log a warning and return `False`. |
| Mutable default argument (W0102) | Bug | 11 | `order_history=[]` is created once and shared by every call, so history leaks between orders. | Default changed to `None`; a new list is created inside the function. |
| Unknown dishes cost 99 (manual) | Logic bug | 15 | `menu.get(i, 99)` makes "sushi" cost 99 and still creates the order. | Reject orders containing dishes that are not on the menu. |
| `VALID_STATUSES` never used (manual) | Logic bug | 9, 21-25 | Status "teleported" was accepted because nothing checked the list. | `update_order_status` now validates against `VALID_STATUSES`. |
| Empty order accepted (manual) | Logic bug | 60, 64 | An order with no customer and no items was created and could be "delivered". | `create_order` rejects an empty customer or empty item list. |
| Overly broad `except Exception` (W0718) | Quality | 32 | Hides unrelated bugs while loading the menu. | Catch only `(OSError, json.JSONDecodeError)`. |
| Files opened without `with` (R1732) and no encoding (W1514) | Quality | 30, 43, 49 | File handles can leak if an error occurs; encoding depends on the OS. | Use `with open(..., encoding="utf-8")`. |
| Global statements (W0603) | Design | 12, 28, 48 | Functions change module-level state, which is hard to test and reason about. | Moved `orders`, `menu` and `next_id` into an `OrderQueue` class. |
| Bad names (C0103) | Style | 7, 51 | `next_id` is treated as a constant; `printQueue` is not snake_case. | `next_id` is now an attribute; `printQueue` renamed to `print_queue`. |
| `%` string formatting (C0209) | Style | 52 | Old-style formatting. | Replaced with an f-string. |
| Missing docstrings (C0114, C0116) | Documentation | 1, 11, 21, 27, 35, 42, 47, 51, 56 | No module or function documentation. | Added a docstring to the module, class and every method. |
| Missing blank lines (E302, E305) | Style (PEP 8) | 11, 21, 27, 35, 42, 47, 51, 56, 70 | PEP 8 needs two blank lines around top-level definitions. | Added the blank lines. |
| Lines too long (E501) | Style (PEP 8) | 16, 54 | Lines are 96 and 80 characters; limit is 79. | Wrapped the lines. |
| `main()` runs on import (manual) | Design | 70 | Importing the file would immediately run the demo. | Added `if __name__ == "__main__":`. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 6.27/10 (22 messages) | 10.00/10 |
| Bandit | 3 issues (1 Medium, 2 Low) | No issues |
| Flake8 | 12 violations | 0 |
