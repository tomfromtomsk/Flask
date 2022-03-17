# flask_rest_api

## Api

### kwargs should have been in definition(), not decorator.

```python
class Api(flask_rest_api.Api):
    def definition(self, name, **kwargs):
```

## Blueprint

### operation tags should be appended, not replaced.

```python
            # Tag all operations with Blueprint name
            # Format operations documentation in OpenAPI structure
            for operation in doc.values():
                operation['tags'] = [self.name]
```


## EnumField

### metadata not exported to OpenAPI (#24)

```python
        self.metadata['enum']
```
