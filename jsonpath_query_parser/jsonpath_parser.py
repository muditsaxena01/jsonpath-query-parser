import ctypes
import re
import traceback
from copy import deepcopy

from jsonpath_ng.ext import parse


class JSONPathParser:
    '''JSONPathParser is a thin wrapper on top of jsonpath_ng (see https://github.com/h2non/jsonpath-ng)
    library which provides additional features like boolean queries and lazy depth first tree traversal to
    build the tree where each traversed node path is kept in a map as key value, where key stores the
    jsonPath of each traversed node and value is a pointer to it's value, to make consecutive jsonPath
    evaluations on the same object faster.

    Additional Boolean Features
        AND: Consecutive JSON-path evaluation on matches returned in (n - 1)th iteration
            and returns matches after evaluating final path in the clause
        OR: Provides collective list of matches after evaluating all JSON-paths in the
            clause
        CONDITIONAL_AND: Consecutive JSON-path evaluation on source object and returns
            original object if all paths in the clause return non empty values
        CONDITIONAL_OR: Consecutive JSON-path evaluation on source object and returns
            original object if any of the paths in the clause return non empty value
    '''

    def __init__(self, obj):
        '''Constructor accepting JSON-like (python dict + list) objects on which JSON-path
        evaluation need to be performed.

        Constructor initializes the source object, regular expressions to parse the JSON-path
        expressions

        Args:
            obj: JSON-like object on which perform JSON-paths evaluations
        '''
        self.obj = obj
        self.parsing_regex = re.compile("((\.[^\d\W]\w*)|((\.?)([^\d\W]\w*)?\[.+?(?=(\]))\]))")
        self.dereferencing_map = {'$': [id(self.obj)]}

    def _dereference(self, path):
        '''Method to dereference value located at the given JSON-path expression

        This method has 3 key responsibilities:
            1. To parse the given JSON-path string to extract location of each intermediate node
                along the path
            2. Run depth first traversal and build pointer map at each intermediate node if that node
                has not already been encountered before.
            3. Return value at the final node in the path

        Args:
            path: JSON-path string to be dereferenced in the source object

        Returns:
            List of matches against the given JSON-path

        Raises:
            Exception (Parse error): if provided jsonpath does not conform to the syntax
        '''
        path_to_traverse = [match[0] for match in self.parsing_regex.findall(path)]

        for depth in range(1, len(path_to_traverse) + 1):

            node_path = '$' + ''.join(path_to_traverse[0: depth])

            if node_path not in self.dereferencing_map:
                parent_node_path = ('$' + ''.join(path_to_traverse[0: depth - 1]))
                source_object_list = self.dereferencing_map[parent_node_path]

                expr = parse('$' + path_to_traverse[depth - 1])
                matches = [
                    id(match.value) for source_object in source_object_list for match in expr.find(
                        ctypes.cast(source_object, ctypes.py_object).value
                    )
                ]

                self.dereferencing_map[node_path] = matches

        return [ctypes.cast(match, ctypes.py_object).value for match in self.dereferencing_map[path]]

    def parse(self, path, return_array=False, not_null=True, temp_obj=None):
        '''Method to be used to evaluate JSONPath Expressions or Queries with optional flags

        This method is mainly responsible for adding wrapper that provides boolean queries on jsonPath
        expressions

        Args:
            path: JSON-path expression or Query with nested boolean clauses
            return_array: Boolean flag specifying if all matches are to be returned or just the first one
            not_null: Boolean flag specifying if null values are to be omitted for OR/CONDITIONAL_OR queries
        '''
        matches = []

        obj = temp_obj or self.obj

        if isinstance(path, dict):
            if 'OR' in path and isinstance(path.get('OR'), list) and path.get('OR'):
                for or_path in path.get('OR'):
                    matches += self.parse(or_path, True, not_null, obj)

            elif 'AND' in path and isinstance(path.get('AND'), list) and path.get('AND'):
                and_matches = deepcopy(self.obj)
                for and_path in path.get('AND'):
                    and_matches = self.parse(and_path, True, not_null, and_matches)
                return and_matches if return_array else (and_matches or [None])[0]

            elif (
                    'CONDITIONAL_OR' in path and isinstance(path.get('CONDITIONAL_OR'), list) and
                    path.get('CONDITIONAL_OR')
            ):
                for or_path in path.get('CONDITIONAL_OR'):
                    matched_value = self.parse(or_path, True, not_null)
                    if matched_value:
                        matches += matched_value

            elif (
                    'CONDITIONAL_AND' in path and isinstance(path.get('CONDITIONAL_AND'), list) and
                    path.get('CONDITIONAL_AND')
            ):
                and_matches = self.obj
                for and_path in path.get('CONDITIONAL_AND'):
                    and_matches = and_matches if self.parse(and_path, True, not_null, and_matches) else {}
                return and_matches if return_array else (and_matches or [None])[0]

            elif 'jsonPath' in path and isinstance(path.get('jsonPath'), str):
                path = path.get('jsonPath', '')
                path = path.format(root='$')
                paths = path.split('|')
                for path in paths:
                    matches.extend([
                        match for match in self._dereference(path) if match is not None or (not not_null)
                    ])

        elif isinstance(path, str):
            path = path.format(root='$')
            paths = path.split('|')

            for path in paths:
                matches.extend([
                    match for match in self._dereference(path) if match is not None or (not not_null)
                ])

        if return_array:
            return matches or []

        return (matches or [None])[0]
