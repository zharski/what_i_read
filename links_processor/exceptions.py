class LinksProcessorError(Exception):
    """Base exception for links processor errors."""
    pass


class FileParsingError(LinksProcessorError):
    """Raised when a file cannot be parsed."""
    def __init__(self, file_path: str, message: str):
        self.file_path = file_path
        super().__init__(f"Error parsing {file_path}: {message}")


class InvalidFileNameError(LinksProcessorError):
    """Raised when a filename doesn't match the expected pattern."""
    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"Invalid filename format: {filename}. Expected YYYY-MM.md")


class OutputError(LinksProcessorError):
    """Raised when output cannot be written."""
    def __init__(self, output_path: str, message: str):
        self.output_path = output_path
        super().__init__(f"Error writing to {output_path}: {message}") 