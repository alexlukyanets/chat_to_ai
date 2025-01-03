# Built-ins
from fnmatch import fnmatch
from os import path, walk, sep
from os.path import basename

# Project
from scripts import consts


def read_gitignore_patterns(path_to_gitignore: str) -> list[str]:
    """
    Parse .gitignore file lines into a list of patterns.
    """
    patterns: list[str] = []
    with open(path_to_gitignore, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                patterns.append(line)
    return patterns


def match_patterns(item_path: str, ignore_patterns: list[str]) -> bool:
    """
    Check if a path matches any of the ignore patterns or is the .git folder.
    """
    for pattern in ignore_patterns:
        if fnmatch(item_path, pattern) or fnmatch(basename(item_path), pattern):
            return True
    return False


def list_files(start_path: str, ignore_patterns: list[str]) -> None:
    """
    Recursively list files in a directory while respecting ignore patterns.
    """
    for root, dirs, files in walk(start_path, topdown=True):
        dirs[:] = [
            d
            for d in dirs
            if not match_patterns(
                item_path=path.join(root, d),
                ignore_patterns=ignore_patterns
            )
               and d != consts.IGNORE_GIT
        ]
        files[:] = [
            f
            for f in files
            if not match_patterns(
                item_path=path.join(root, f),
                ignore_patterns=ignore_patterns
            )
        ]

        level: int = root.replace(start_path, '').count(sep)
        indent: str = ' ' * 4 * level
        print(f'{indent}{path.basename(root)}/')

        sub_indent: str = ' ' * 4 * (level + 1)
        for d in dirs[:consts.MAX_LISTING]:
            print(f'{sub_indent}{d}/')
        if len(dirs) > consts.MAX_LISTING:
            print(f'{sub_indent}... and more directories')

        for f in files[:consts.MAX_LISTING]:
            print(f'{sub_indent}{f}')
        if len(files) > consts.MAX_LISTING:
            print(f'{sub_indent}... and more files')


def main() -> None:
    """
    Main entry point for listing files ignoring .git and .gitignore patterns.
    """
    project_path: str = consts.DEFAULT_PROJECT_PATH
    gitignore_path: str = path.join(project_path, consts.GITIGNORE_FILE)

    ignore_patterns: list[str] = [consts.IGNORE_GIT]
    if path.exists(gitignore_path):
        ignore_patterns += read_gitignore_patterns(path_to_gitignore=gitignore_path)

    list_files(
        start_path=project_path,
        ignore_patterns=ignore_patterns
    )


if __name__ == '__main__':
    main()
