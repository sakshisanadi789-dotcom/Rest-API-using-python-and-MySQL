import shutil
from pathlib import Path


TEXT_FILES_DIRECTORY = Path(__file__).resolve().parent / "uploads" / "text"


class InvalidFileNameError(ValueError):
    """Raised when a requested text filename is outside the allowed format."""


def get_text_file_path(filename: str) -> Path:
    if (
        not filename
        or filename in {".", ".."}
        or "/" in filename
        or "\\" in filename
        or Path(filename).name != filename
        or Path(filename).suffix.lower() != ".txt"
    ):
        raise InvalidFileNameError(
            "Use a simple filename ending in .txt; folder paths are not allowed."
        )

    project_directory = Path(__file__).resolve().parent
    directory = TEXT_FILES_DIRECTORY.resolve()
    try:
        directory.relative_to(project_directory)
    except ValueError as error:
        raise InvalidFileNameError("The text folder must stay inside the project.") from error
    directory.mkdir(parents=True, exist_ok=True)
    directory = directory.resolve()
    try:
        directory.relative_to(project_directory)
    except ValueError as error:
        raise InvalidFileNameError("The text folder must stay inside the project.") from error

    file_path = (directory / filename).resolve()
    try:
        file_path.relative_to(directory)
    except ValueError as error:
        raise InvalidFileNameError("The requested file is outside the text folder.") from error
    return file_path


def create_text_file(filename: str) -> str:
    file_path = get_text_file_path(filename)
    with file_path.open("x", encoding="utf-8"):
        pass
    return filename


def write_text_file(filename: str, content: str) -> int:
    file_path = get_text_file_path(filename)
    return file_path.write_text(content, encoding="utf-8")


def append_text_file(filename: str, content: str) -> int:
    file_path = get_text_file_path(filename)
    with file_path.open("a", encoding="utf-8") as text_file:
        return text_file.write(content)


def read_text_file(filename: str) -> str:
    file_path = get_text_file_path(filename)
    return file_path.read_text(encoding="utf-8")


def read_text_file_lines(filename: str) -> list[str]:
    return read_text_file(filename).splitlines()


def text_file_exists(filename: str) -> bool:
    return get_text_file_path(filename).is_file()


def rename_text_file(filename: str, new_filename: str) -> str:
    source_path = get_text_file_path(filename)
    destination_path = get_text_file_path(new_filename)
    source_path.rename(destination_path)
    return new_filename


def copy_text_file(filename: str, copy_filename: str) -> str:
    source_path = get_text_file_path(filename)
    destination_path = get_text_file_path(copy_filename)

    with source_path.open("rb") as source_file:
        with destination_path.open("xb") as copy_file:
            try:
                shutil.copyfileobj(source_file, copy_file)
            except OSError:
                copy_file.close()
                destination_path.unlink(missing_ok=True)
                raise
    return copy_filename


def delete_text_file(filename: str) -> None:
    get_text_file_path(filename).unlink()


def get_text_file_size(filename: str) -> int:
    return get_text_file_path(filename).stat().st_size
