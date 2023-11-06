## Testing

This app has unit tests which are run automatically in GitHub Actions. If you are making changes, please run them:

```
inv test
```

To run specific tests

```
docker-compose -f docker/docker-compose.local.yml run --rm test bash
pytest path/to/test.py -vv
```
