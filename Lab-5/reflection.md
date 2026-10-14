# Reflection

## 1. Which issues were easiest and which were hardest to fix?

The Flake8 formatting issues were the easiest: adding blank lines and wrapping two long lines. Removing the bare `except` and the mutable default argument were also quick once I understood why they are dangerous. The hardest was removing the `global` statements, because it meant restructuring the program into an `OrderQueue` class. Replacing pickle with JSON also had a catch: JSON turns integer dictionary keys into strings, so restoring orders needed a conversion and `next_id` had to be reset.

## 2. Did the tools report any false positives, and how would you handle them?

I did not find any real false positives. Some findings overlapped: Bandit reported pickle twice (B403 and B301) and the bare `except` was reported by Bandit, Pylint and Flake8, but all pointed at real problems. If a warning really were a false positive, I would suppress only that line, for example with `# nosec` or `# pylint: disable=...`, and add a comment explaining why it is safe, instead of disabling the check everywhere.

## 3. How could you integrate static analysis into a real development workflow?

I would run the tools automatically so nobody has to remember: as a pre-commit hook that checks code before each commit, and in a CI pipeline (for example GitHub Actions) that fails a pull request if Flake8 or Bandit report issues or the Pylint score drops below a set threshold. Editors can also show warnings while typing.

## 4. What improvements did you see in code quality, security and robustness?

Pylint went from 6.27 to 10.00, Bandit went from 3 issues to none, and Flake8 went from 12 violations to none. The code is safer (no unpickling), more robust (errors are logged instead of hidden, bad input is rejected) and easier to read and test (docstrings, no global state, clear names). The tools also did not catch some real bugs, such as unknown dishes costing 99 and the unused `VALID_STATUSES`; I found those by running and reading the program, so static analysis supports but does not replace testing and code review.
