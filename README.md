# TCP
### Client request package
Bytes: JSON-file with request:
```
  {
    "actions": {<name>: <value>,...},
    "observations": [<value_1>, ...],
  }
```
### Server response package
Bytes: JSON-file with request:
```
  {
    "actions": SUCCESS / FAILED,
    "observations": {<name>: <value>, ...},
  }
```