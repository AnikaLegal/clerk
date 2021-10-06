## Testing and Linting

This app has unit tests which are run automatically in GitHub Actions. If you are making changes, please run them:

```
make test
```

To run specific tests

```
docker-compose -f docker/docker-compose.local.yml run --rm test bash
pytest case/tests/test_urls.py -vv
```

The Python code is formatted with Black. To check the code with the linter run:

```
make lint
```

To automatically fix any linting errors, run:

```
make format
```
