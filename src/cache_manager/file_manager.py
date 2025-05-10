import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Union


class FileManager:
    """
    A centralized manager for file I/O operations within a specified base resources directory.
    All paths are relative to this resources directory.
    """

    def __init__(self, resources_dir_rel_to_root: str = "../../resources"):
        """
        Initialize the FileManager.
        
        Args:
            resources_dir_rel_to_root: Path to the base resources directory,
                                       relative to the project root.
        """
        # Resolve the path to ensure it's absolute and normalized
        self.resources_dir = Path(resources_dir_rel_to_root).resolve()
        self._ensure_dir_exists(self.resources_dir)
        print(f"FileManager initialized. Resources directory: {self.resources_dir}")

    def _ensure_dir_exists(self, dir_path: Path) -> None:
        """Ensure that the specified directory exists."""
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_path}")

    def _get_full_path(self, filename: str) -> Path:
        """
        Get the full path for a file within the resources directory.
        
        Args:
            filename: The name of the file, can include subdirectories
                      relative to the resources directory.
                      e.g., "data.json" or "subdir/data.json"
            
        Returns:
            Absolute Path object for the file.
        """
        path_suffix = Path(filename)

        if path_suffix.is_absolute():
            print(f"Warning: Absolute path provided for filename ({filename}). "
                  f"This is usually not intended when using FileManager. "
                  f"The path will be used as is, ignoring the base resources_dir.")
            if not path_suffix.parent.exists():
                self._ensure_dir_exists(path_suffix.parent)
            return path_suffix

        full_path = self.resources_dir / path_suffix

        self._ensure_dir_exists(full_path.parent)

        return full_path

    def read_text(self, filename: str, encoding: str = "utf-8") -> str:
        """Read text content from a file in the resources directory."""
        full_path = self._get_full_path(filename)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        return full_path.read_text(encoding=encoding)

    def write_text(self, filename: str, content: str, encoding: str = "utf-8") -> str:
        """Write text content to a file in the resources directory."""
        full_path = self._get_full_path(filename)
        with open(full_path, 'w', encoding=encoding) as f:
            f.write(content)
        print(f"Text written to: {full_path}")
        return str(full_path)

    def write_json(self, filename: str, data: Union[Dict, List], indent: int = 2,
                   encoding: str = "utf-8") -> str:
        """Write data as JSON to a file in the resources directory."""
        full_path = self._get_full_path(filename)
        with open(full_path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent)
        print(f"Data written to: {full_path}")
        return str(full_path)

    def read_json(self, filename: str, encoding: str = "utf-8") -> Union[Dict, List]:
        """Read JSON data from a file in the resources directory."""
        full_path = self._get_full_path(filename)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        with open(full_path, 'r', encoding=encoding) as f:
            return json.load(f)

    def write_csv(self, filename: str, data: List[List], header: Optional[List[str]] = None,
                  encoding: str = "utf-8") -> str:
        """Write data as CSV to a file in the resources directory."""
        full_path = self._get_full_path(filename)
        with open(full_path, 'w', newline='', encoding=encoding) as f:
            writer = csv.writer(f)
            if header:
                writer.writerow(header)
            writer.writerows(data)
        print(f"Data written to: {full_path}")
        return str(full_path)

    def read_csv(self, filename: str, has_header: bool = False,
                 encoding: str = "utf-8") -> Union[List[List[str]], List[Dict[str, str]]]:
        """Read CSV data from a file in the resources directory."""
        full_path = self._get_full_path(filename)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")

        with open(full_path, 'r', newline='', encoding=encoding) as f:
            reader = csv.reader(f)
            if has_header:
                try:
                    header_row = next(reader)
                except StopIteration:
                    print(f"Warning: CSV file {full_path} is empty or has no header.")
                    return []

                data_rows = list(reader)
                result = []
                for row in data_rows:
                    row_dict = {header_row[i]: row[i] if i < len(row) else None for i in range(len(header_row))}
                    result.append(row_dict)
                return result
            else:
                return list(reader)

    def file_exists(self, filename: str) -> bool:
        """Check if a file exists in the resources directory."""
        full_path = self._get_full_path(filename)
        return full_path.exists()


# Instantiate the FileManager for global use
# The default resources_dir is "../resources" relative to the project root
file_manager = FileManager()
