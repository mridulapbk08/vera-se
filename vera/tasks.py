from vera.task_config import BenchmarkTask


TASKS = [
    BenchmarkTask(
        task_id="task_1_percentage",
        repo_path="benchmarks/task_1_percentage/source",
        hidden_tests_path="benchmarks/task_1_percentage/hidden",
        oracle_tests_path="benchmarks/task_1_percentage/oracle",
        source_file="calculator.py",
        target_function="percentage",
        bug_description="""
The percentage function returns a ratio instead of a percentage.

percentage(25, 100)

should return 25.
""",
    ),

    BenchmarkTask(
        task_id="task_2_string",
        repo_path="benchmarks/task_2_string/source",
        hidden_tests_path="benchmarks/task_2_string/hidden",
        oracle_tests_path="benchmarks/task_2_string/oracle",
        source_file="text_utils.py",
        target_function="normalize_name",
        bug_description="""
normalize_name should lowercase a name and remove
leading and trailing whitespace.

normalize_name("  Alice  ")

should return "alice".
""",
    ),

    BenchmarkTask(
        task_id="task_3_list",
        repo_path="benchmarks/task_3_list/source",
        hidden_tests_path="benchmarks/task_3_list/hidden",
        oracle_tests_path="benchmarks/task_3_list/oracle",
        source_file="list_utils.py",
        target_function="last_item",
        bug_description="""
last_item should return the final element of a list.

last_item([1, 2, 3])

should return 3.
""",
    ),

    BenchmarkTask(
        task_id="task_4_dict",
        repo_path="benchmarks/task_4_dict/source",
        hidden_tests_path="benchmarks/task_4_dict/hidden",
        oracle_tests_path="benchmarks/task_4_dict/oracle",
        source_file="dict_utils.py",
        target_function="get_value",
        bug_description="""
get_value should retrieve a value from a dictionary
without modifying the dictionary.

If the key does not exist, it should return the
provided default value.

Example:

data = {"name": "Alice"}

get_value(data, "name")

should return "Alice" and must not remove the
"name" key from data.
""",
    ),

    BenchmarkTask(
        task_id="task_5_format",
        repo_path="benchmarks/task_5_format/source",
        hidden_tests_path="benchmarks/task_5_format/hidden",
        oracle_tests_path="benchmarks/task_5_format/oracle",
        source_file="format_utils.py",
        target_function="clean_label",
        bug_description="""
clean_label should lowercase a label and remove
only leading and trailing whitespace.

It should preserve meaningful characters and
spacing inside the label.

clean_label("  Hello World  ")

should return "hello world".
""",
    ),

    BenchmarkTask(
        task_id="task_6_numeric",
        repo_path="benchmarks/task_6_numeric/source",
        hidden_tests_path="benchmarks/task_6_numeric/hidden",
        oracle_tests_path="benchmarks/task_6_numeric/oracle",
        source_file="math_utils.py",
        target_function="average",
        bug_description="""
average should return the arithmetic mean of
two numeric values.

average(10, 20)

should return 15.

The calculation should preserve decimal precision
and work for positive, negative, and fractional
values.
""",
    ),
]