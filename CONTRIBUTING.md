# Contributing

## Branches

- `main` is always in a working state.
- Work on short-lived branches named `<type>/<short-description>`, for example `feat/sound-classifier-runner` or `docs/evaluation-plan`.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <summary in the imperative, lower case, no full stop>
```

- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `build`, `perf`.
- Scopes: `app`, `sketch`, `models`, `data`, `hardware`, `scripts`, `tests`, `docs`.
- Keep the summary under 72 characters. Add a body when the reason for the change is not obvious.
- One logical change per commit.

## What not to commit

- Edge Impulse model binaries (`*.eim`). Record the SHA-256 in `models/CHECKSUMS.txt` instead.
- Raw recordings, images or videos of people. Document datasets in `data/` instead.
- Secrets, API keys and `.env` files.

## Code and documentation style

- Python follows PEP 8, formatted with 4-space indentation. Use type hints on public functions.
- Arduino sketches use 2-space indentation and avoid blocking calls in `loop()`.
- Every number in the documentation says how it was measured and on what hardware.
- Define an acronym the first time it appears in a document.

## Tests

Run `pytest` from the repository root before opening a pull request. Add a test with each fix to the game logic, the line validator or the Bridge contract.
