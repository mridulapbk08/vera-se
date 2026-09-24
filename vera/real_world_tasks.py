from vera.real_world_task import RealWorldTask


REAL_WORLD_TASKS = [
    RealWorldTask(
        task_id="bugsinpy_black_1",
        repo_path="/Users/mridulaprabhakar/bugsinpy-work/black-1/black",
        source_file="black.py",
        bug_description="""Black crashes when formatting multiple files in an environment where
ProcessPoolExecutor cannot be created and raises OSError.

The reformat_many function should gracefully fall back to mono-process
execution when multiprocessing is unavailable, while preserving normal
multiprocessing behavior on supported systems.""",
        visible_test_command=[
            "python",
            "-m",
            "unittest",
            "-q",
            "tests.test_black.BlackTestCase.test_works_in_mono_process_only_environment",
        ],
        oracle_test_path="real_world_oracles/black_1/test_black_1_oracle.py",
        repair_type="function",
        target_function="reformat_many",
    ),

    RealWorldTask(
        task_id="bugsinpy_black_3",
        repo_path="/Users/mridulaprabhakar/bugsinpy-work/black-3/black",
        source_file="black.py",
        bug_description="""Black does not correctly reject a nonexistent path supplied through
the --config command-line option.

When --config points to a file that does not exist, Black should treat
the path as invalid input and return the standard command-line usage
error code instead of attempting to read the missing configuration file.""",
        visible_test_command=[
            "python",
            "-m",
            "unittest",
            "-q",
            "tests.test_black.BlackTestCase.test_invalid_config_return_code",
        ],
        oracle_test_path="real_world_oracles/black_3/test_black_3_oracle.py",
        repair_type="region",
        region_start_line=394,
        region_end_line=402,
    ),

    RealWorldTask(
        task_id="bugsinpy_black_4",
        repo_path="/Users/mridulaprabhakar/bugsinpy-work/black-4/black",
        source_file="black.py",
        bug_description="""Black can incorrectly preserve or introduce empty lines at the
beginning of a Python file when the input begins with a backslash
followed by whitespace.

Formatting should not produce unnecessary blank lines at the
beginning of the file, while preserving Black's normal empty-line
handling for the rest of the file.""",
        visible_test_command=[
            "python",
            "-m",
            "unittest",
            "-q",
            "tests.test_black.BlackTestCase.test_beginning_backslash",
        ],
        oracle_test_path="real_world_oracles/black_4/test_black_4_oracle.py",
        repair_type="region",
        region_start_line=1476,
        region_end_line=1486,
    ),

    RealWorldTask(
        task_id="bugsinpy_black_7",
        repo_path="/Users/mridulaprabhakar/bugsinpy-work/black-7/black",
        source_file="black.py",
        bug_description="""Black formats long tuple-unpacking assignments incorrectly.

When the left-hand side of an assignment contains a long tuple of
variables that exceeds the line length, Black should place that tuple
inside parentheses and format the variables across multiple lines,
rather than splitting only the right-hand side.

Normal short tuple assignments and unrelated assignment formatting
should continue to behave normally.""",
        visible_test_command=[
            "python",
            "-m",
            "unittest",
            "-q",
            "tests.test_black.BlackTestCase.test_tuple_assign",
        ],
        oracle_test_path="real_world_oracles/black_7/test_black_7_oracle.py",
        repair_type="function",
        target_function="normalize_invisible_parens",
    ),

    RealWorldTask(
        task_id="bugsinpy_black_8",
        repo_path="/Users/mridulaprabhakar/bugsinpy-work/black-8/black",
        source_file="black.py",
        bug_description="""Black can place a trailing comma incorrectly when formatting
parenthesized import statements that contain trailing comments.

When the final imported name does not already have a comma and comments
follow it, the comma should be placed after the imported name rather than
after the comments.

Existing commas, comments, and normal import formatting should continue
to be preserved.""",
        visible_test_command=[
            "python",
            "-m",
            "unittest",
            "-q",
            "tests.test_black.BlackTestCase.test_comments7",
        ],
        oracle_test_path="real_world_oracles/black_8/test_black_8_oracle.py",
        repair_type="function",
        target_function="bracket_split_build_line",
    ),

    RealWorldTask(
        task_id="bugsinpy_black_9",
        repo_path="/Users/mridulaprabhakar/bugsinpy-work/black-9/black",
        source_file="black.py",
        bug_description="""Black can fail to parse Python 2 source files that enable
print_function through a __future__ import.

When Python 2 is the selected target version and the source uses
from __future__ import print_function, Black should support
function-style print calls such as print(value, file=stream).

Normal Python 2 print statements and Python 3 grammar selection
should continue to work correctly.""",
        visible_test_command=[
            "python",
            "-m",
            "unittest",
            "-q",
            "tests.test_black.BlackTestCase.test_python2_print_function",
        ],
        oracle_test_path="real_world_oracles/black_9/test_black_9_oracle.py",
        repair_type="function",
        target_function="get_grammars",
    ),

    RealWorldTask(
        task_id="bugsinpy_black_10",
        repo_path="/Users/mridulaprabhakar/bugsinpy-work/black-10/black",
        source_file="blib2to3/pgen2/driver.py",
        bug_description="""Black handles comment indentation inconsistently when source
indentation uses tabs.

Tab-indented code and equivalent space-indented code should produce
the same formatted output, including comments at different nesting
levels.

Existing behavior for space-indented code should remain unchanged.""",
        visible_test_command=[
            "python",
            "-m",
            "unittest",
            "-q",
            "tests.test_black.BlackTestCase.test_comment_indentation",
        ],
        oracle_test_path="real_world_oracles/black_10/test_black_10_oracle.py",
        repair_type="region",
        region_start_line=117,
        region_end_line=144,
    ),

    RealWorldTask(
        task_id="bugsinpy_black_13",
        repo_path="/Users/mridulaprabhakar/bugsinpy-work/black-13/black",
        source_file="blib2to3/pgen2/tokenize.py",
        bug_description="""Black cannot correctly parse Python 3.7-style async generator
expressions that use async for.

Async generator expressions should be parsed and formatted correctly,
while ordinary generator expressions and async function definitions
should continue to behave normally.""",
        visible_test_command=[
            "python",
            "-m",
            "unittest",
            "-q",
            "tests.test_black.BlackTestCase.test_python37",
        ],
        oracle_test_path="real_world_oracles/black_13/test_black_13_oracle.py",
        repair_type="function",
        target_function="generate_tokens",
    ),

    RealWorldTask(
        task_id="bugsinpy_black_14",
        repo_path="/Users/mridulaprabhakar/bugsinpy-work/black-14/black",
        source_file="black.py",
        bug_description="""Black does not correctly identify __future__ imports when imported
features use aliases or are combined with other imported future features.

The original feature names should be detected regardless of aliases,
while normal future imports and non-future imports should retain their
existing behavior.""",
        visible_test_command=[
            "python",
            "-m",
            "unittest",
            "-q",
            "tests.test_black.BlackTestCase.test_get_future_imports",
        ],
        oracle_test_path="real_world_oracles/black_14/test_black_14_oracle.py",
        repair_type="function",
        target_function="get_future_imports",
    ),

    RealWorldTask(
        task_id="bugsinpy_black_16",
        repo_path="/Users/mridulaprabhakar/bugsinpy-work/black-16/black",
        source_file="black.py",
        bug_description="""Black can fail while recursively discovering Python files when a
symbolic link resolves to a path outside the configured root directory.

Symbolic links pointing outside the root should be ignored without
crashing. Unexpected non-symbolic-link paths outside the root should
continue to raise an error, and normal files inside the root should
continue to be discovered.""",
        visible_test_command=[
            "python",
            "-m",
            "unittest",
            "-q",
            "tests.test_black.BlackTestCase.test_symlink_out_of_root_directory",
        ],
        oracle_test_path="real_world_oracles/black_16/test_black_16_oracle.py",
        repair_type="function",
        target_function="gen_python_files_in_dir",
    ),
]