# JSONPath Query Parser

JSONPathParser is a thin wrapper on top of jsonpath_ng (see https://github.com/h2non/jsonpath-ng)
library which provides additional features like boolean queries and lazy depth first tree traversal to
build the tree where each traversed node path is kept in a map as key value, where key stores the
jsonPath of each traversed node and value is a pointer to it's value, to make **consecutive JSONPath
evaluations on the same object** faster.

### Additional Boolean Operators

- AND: Consecutive JSON-path evaluation on matches returned in (n - 1)th iteration
    and returns matches after evaluating final path in the clause
- OR: Provides collective list of matches after evaluating all JSON-paths in the clause
- CONDITIONAL_AND: Consecutive JSON-path evaluation on source object and returns
    original object if all paths in the clause return non empty values
- CONDITIONAL_OR: Consecutive JSON-path evaluation on source object and returns
    original object if any of the paths in the clause return non empty value

#### This project is being pushed to pip. Until then please execute following steps


### Installation Steps
1. Create python 3 virtualenv
```virtualenv -p <Python3 Command or installation path> venv```
2. Activate virtualenv
```source venv/bin/active```
3. Install package dependencies
```pip install -r requirements.txt```

### Usage

Here is a basic example. This documentation is being expanded. Please read through the docstrings for deeper understanding.

```
from jsonpath_query_parser import JSONPathParser

obj = {
    'a': {
        'b': [
            {
                'f': 0,
                'g': True
            },
            {
                'f': 1,
                'g': False
            }
        ]
    }
}

parser = JSONPathParser(obj)

path = '$.a.b[?(@.f == 0)].g'

parser.parse(path)
```

Here `path` can take either a JSONPath expression or a query (use of Additional Boolean Operators)