## Testing

This app has unit tests which are run automatically in GitHub Actions. If you are making changes, please run them:

```
inv test
```

To run specific tests

```
inv test -i
pytest path/to/test.py -vv
```
