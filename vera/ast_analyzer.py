import ast


class ASTAnalyzer:
    @staticmethod
    def parse_code(code: str):
        try:
            return ast.parse(code)
        except SyntaxError:
            return None

    @staticmethod
    def get_function_names(code: str):
        tree = ASTAnalyzer.parse_code(code)

        if tree is None:
            return set()

        functions = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                functions.add(node.name)

        return functions

    @staticmethod
    def get_function_sources(code: str):
        tree = ASTAnalyzer.parse_code(code)

        if tree is None:
            return {}

        lines = code.splitlines()
        functions = {}

        for node in ast.walk(tree):
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                start = node.lineno - 1

                end = getattr(
                    node,
                    "end_lineno",
                    node.lineno,
                )

                source = "\n".join(
                    lines[start:end]
                )

                functions[node.name] = source

        return functions

    @staticmethod
    def changed_functions(
        original: str,
        modified: str,
    ):
        original_functions = (
            ASTAnalyzer.get_function_sources(
                original
            )
        )

        modified_functions = (
            ASTAnalyzer.get_function_sources(
                modified
            )
        )

        all_names = (
            set(original_functions)
            | set(modified_functions)
        )

        changed = set()

        for name in all_names:
            original_source = (
                original_functions.get(name)
            )

            modified_source = (
                modified_functions.get(name)
            )

            if original_source != modified_source:
                changed.add(name)

        return changed