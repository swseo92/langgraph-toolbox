"""
File system service for reading/writing research outputs.

Provides safe file operations with directory management and
content validation for research workflows.
"""

import os
from pathlib import Path
from typing import Optional
import json


class FileSystemService:
    """
    Safe file system operations for research workflows.

    Handles reading, writing, and organizing research outputs
    with automatic directory creation and error handling.

    Example:
        >>> fs = FileSystemService(base_dir="./research_outputs")
        >>> fs.write_text("report.md", "# Research Report\\n...")
        >>> content = fs.read_text("report.md")
    """

    def __init__(self, base_dir: str = "./research_outputs"):
        """
        Initialize file system service.

        Args:
            base_dir: Base directory for all file operations
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_text(
        self,
        filename: str,
        content: str,
        subdirectory: Optional[str] = None
    ) -> Path:
        """
        Write text content to file.

        Args:
            filename: Name of the file
            content: Text content to write
            subdirectory: Optional subdirectory path

        Returns:
            Path to the written file

        Example:
            >>> fs.write_text("notes.txt", "Important findings...", subdirectory="session_1")
        """
        if subdirectory:
            file_path = self.base_dir / subdirectory / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            file_path = self.base_dir / filename

        file_path.write_text(content, encoding="utf-8")
        return file_path

    def read_text(
        self,
        filename: str,
        subdirectory: Optional[str] = None
    ) -> str:
        """
        Read text content from file.

        Args:
            filename: Name of the file
            subdirectory: Optional subdirectory path

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist

        Example:
            >>> content = fs.read_text("report.md")
        """
        if subdirectory:
            file_path = self.base_dir / subdirectory / filename
        else:
            file_path = self.base_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return file_path.read_text(encoding="utf-8")

    def write_json(
        self,
        filename: str,
        data: dict,
        subdirectory: Optional[str] = None,
        indent: int = 2
    ) -> Path:
        """
        Write JSON data to file.

        Args:
            filename: Name of the file (will add .json if not present)
            data: Dictionary to serialize
            subdirectory: Optional subdirectory path
            indent: JSON indentation (default: 2)

        Returns:
            Path to the written file

        Example:
            >>> fs.write_json("results.json", {"findings": [...], "confidence": 0.9})
        """
        if not filename.endswith(".json"):
            filename = f"{filename}.json"

        content = json.dumps(data, indent=indent, ensure_ascii=False)
        return self.write_text(filename, content, subdirectory)

    def read_json(
        self,
        filename: str,
        subdirectory: Optional[str] = None
    ) -> dict:
        """
        Read JSON data from file.

        Args:
            filename: Name of the file
            subdirectory: Optional subdirectory path

        Returns:
            Deserialized dictionary

        Example:
            >>> data = fs.read_json("results.json")
            >>> print(data["findings"])
        """
        if not filename.endswith(".json"):
            filename = f"{filename}.json"

        content = self.read_text(filename, subdirectory)
        return json.loads(content)

    def list_files(
        self,
        subdirectory: Optional[str] = None,
        pattern: str = "*"
    ) -> list[Path]:
        """
        List files in directory.

        Args:
            subdirectory: Optional subdirectory path
            pattern: Glob pattern (default: "*" for all files)

        Returns:
            List of Path objects

        Example:
            >>> # List all markdown files
            >>> md_files = fs.list_files(pattern="*.md")
            >>> for file in md_files:
            ...     print(file.name)
        """
        if subdirectory:
            directory = self.base_dir / subdirectory
        else:
            directory = self.base_dir

        if not directory.exists():
            return []

        return sorted(directory.glob(pattern))

    def file_exists(
        self,
        filename: str,
        subdirectory: Optional[str] = None
    ) -> bool:
        """
        Check if file exists.

        Args:
            filename: Name of the file
            subdirectory: Optional subdirectory path

        Returns:
            True if file exists, False otherwise

        Example:
            >>> if fs.file_exists("report.md"):
            ...     content = fs.read_text("report.md")
        """
        if subdirectory:
            file_path = self.base_dir / subdirectory / filename
        else:
            file_path = self.base_dir / filename

        return file_path.exists()

    def delete_file(
        self,
        filename: str,
        subdirectory: Optional[str] = None
    ) -> bool:
        """
        Delete a file.

        Args:
            filename: Name of the file
            subdirectory: Optional subdirectory path

        Returns:
            True if file was deleted, False if it didn't exist

        Example:
            >>> fs.delete_file("temp.txt")
        """
        if subdirectory:
            file_path = self.base_dir / subdirectory / filename
        else:
            file_path = self.base_dir / filename

        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def get_file_size(
        self,
        filename: str,
        subdirectory: Optional[str] = None
    ) -> int:
        """
        Get file size in bytes.

        Args:
            filename: Name of the file
            subdirectory: Optional subdirectory path

        Returns:
            File size in bytes

        Raises:
            FileNotFoundError: If file doesn't exist

        Example:
            >>> size = fs.get_file_size("report.md")
            >>> print(f"Report size: {size / 1024:.2f} KB")
        """
        if subdirectory:
            file_path = self.base_dir / subdirectory / filename
        else:
            file_path = self.base_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return file_path.stat().st_size

    def create_subdirectory(self, subdirectory: str) -> Path:
        """
        Create a subdirectory.

        Args:
            subdirectory: Subdirectory path

        Returns:
            Path to the created directory

        Example:
            >>> fs.create_subdirectory("session_2024_11")
        """
        dir_path = self.base_dir / subdirectory
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
