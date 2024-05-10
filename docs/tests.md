## Testing

Tests are run automatically via GitHub Actions when the `develop` or `master`
branches are pushed.

If you are making changes, please run them locally:

```
inv test
```

This launches a docker container used to run the tests.

To run specific tests, use the `--interactive` flag to open a shell on the
docker container. The `pytest` utility can then be used to run specific tests
directly:

```
inv test -i
pytest -vv path/to/test.py
```

To debug tests using vscode use the `--debug` flag to run the python `debugpy`
debugger on the docker container:

```
inv test -d
```

The debugger will wait for the client to attach. You can attach using the same
vscode launch profile used to debug the Clerk app (see
[here](https://github.com/AnikaLegal/clerk/blob/develop/.vscode/launch.json)).

You can also debug specific tests using the `--interactive` and `--debug` flags
together:

```
inv test -d -i
pytest -vv path/to/test.py
```

> [!NOTE]
> The debugger used for testing and for the Clerk app listens on the same port
> so you can only run one at a time.
