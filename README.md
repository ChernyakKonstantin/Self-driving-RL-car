# TCP
### Client request package
Bytes: JSON-file with request:

1. Environment configuration request:
```
  {
    "configuration": {<name>: <value>,...},
  }
```

2. Environmnet step request:
```
  {
    "actions": {<name>: <value>,...},
    "observations": [<value_1>, ...],
  }
```
### Server response package
Bytes: JSON-file with response:
1. Environment configuration response:
```
  {
    "configuration": {<name>: SUCCESS / FAILED},
  }
```

```
  {
    "actions": SUCCESS / FAILED,
    "observations": {<name>: <value>, ...},
  }
```