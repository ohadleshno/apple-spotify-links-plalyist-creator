import os
import json
import csv
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable


class OutputCache:
    """
    A centralized manager for file I/O operations that ensures all files are saved to and read from
    the outputs directory.
    """
    
    def __init__(self, outputs_dir: str = "outputs"):
        """
        Initialize the output cache.
        
        Args:
            outputs_dir: Path to the outputs directory relative to the project root
        """
        self.outputs_dir = Path(outputs_dir)
        self._ensure_outputs_dir_exists()
    
    def _ensure_outputs_dir_exists(self) -> None:
        """Ensure that the outputs directory exists."""
        if not self.outputs_dir.exists():
            self.outputs_dir.mkdir(parents=True)
    
    def _get_full_path(self, filename: str) -> Path:
        """
        Get the full path for a file in the outputs directory.
        
        Args:
            filename: The name of the file
            
        Returns:
            Path object for the file
        """
        # Handle cases where filename might already include directories
        path = Path(filename)
        
        # If it's an absolute path, warn and use only the filename
        if path.is_absolute():
            print(f"Warning: Absolute path provided ({filename}). Using only the filename.")
            path = Path(path.name)
        
        # Create parent directories if needed
        full_path = self.outputs_dir / path
        if not full_path.parent.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
        return full_path
    
    def write_text(self, filename: str, content: str, encoding: str = "utf-8") -> str:
        """
        Write text content to a file in the outputs directory.
        
        Args:
            filename: Name of the file to write to
            content: Text content to write
            encoding: File encoding (default: utf-8)
            
        Returns:
            Path to the written file
        """
        full_path = self._get_full_path(filename)
        full_path.write_text(content, encoding=encoding)
        return str(full_path)
    
    def read_text(self, filename: str, encoding: str = "utf-8") -> str:
        """
        Read text content from a file in the outputs directory.
        
        Args:
            filename: Name of the file to read from
            encoding: File encoding (default: utf-8)
            
        Returns:
            Text content of the file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        full_path = self._get_full_path(filename)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        return full_path.read_text(encoding=encoding)
    
    def write_binary(self, filename: str, content: bytes) -> str:
        """
        Write binary content to a file in the outputs directory.
        
        Args:
            filename: Name of the file to write to
            content: Binary content to write
            
        Returns:
            Path to the written file
        """
        full_path = self._get_full_path(filename)
        full_path.write_bytes(content)
        return str(full_path)
    
    def read_binary(self, filename: str) -> bytes:
        """
        Read binary content from a file in the outputs directory.
        
        Args:
            filename: Name of the file to read from
            
        Returns:
            Binary content of the file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        full_path = self._get_full_path(filename)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        return full_path.read_bytes()
    
    def write_json(self, filename: str, data: Union[Dict, List], indent: int = 2, 
                  encoding: str = "utf-8") -> str:
        """
        Write data as JSON to a file in the outputs directory.
        
        Args:
            filename: Name of the file to write to
            data: Data to serialize as JSON
            indent: JSON indentation level
            encoding: File encoding (default: utf-8)
            
        Returns:
            Path to the written file
        """
        full_path = self._get_full_path(filename)
        with open(full_path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent)
        return str(full_path)
    
    def read_json(self, filename: str, encoding: str = "utf-8") -> Union[Dict, List]:
        """
        Read JSON data from a file in the outputs directory.
        
        Args:
            filename: Name of the file to read from
            encoding: File encoding (default: utf-8)
            
        Returns:
            Deserialized JSON data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        full_path = self._get_full_path(filename)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        with open(full_path, 'r', encoding=encoding) as f:
            return json.load(f)
    
    def write_csv(self, filename: str, data: List[List], header: Optional[List[str]] = None,
                 encoding: str = "utf-8") -> str:
        """
        Write data as CSV to a file in the outputs directory.
        
        Args:
            filename: Name of the file to write to
            data: List of rows to write to CSV
            header: Optional list of column headers
            encoding: File encoding (default: utf-8)
            
        Returns:
            Path to the written file
        """
        full_path = self._get_full_path(filename)
        with open(full_path, 'w', newline='', encoding=encoding) as f:
            writer = csv.writer(f)
            if header:
                writer.writerow(header)
            writer.writerows(data)
        return str(full_path)
    
    def read_csv(self, filename: str, has_header: bool = False, 
                encoding: str = "utf-8") -> Union[List[List], Dict[str, List]]:
        """
        Read CSV data from a file in the outputs directory.
        
        Args:
            filename: Name of the file to read from
            has_header: Whether the CSV has a header row
            encoding: File encoding (default: utf-8)
            
        Returns:
            List of rows or dict mapping headers to columns if has_header=True
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        full_path = self._get_full_path(filename)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        
        with open(full_path, 'r', newline='', encoding=encoding) as f:
            reader = csv.reader(f)
            if has_header:
                header = next(reader)
                data = list(reader)
                result = {h: [row[i] for row in data] for i, h in enumerate(header)}
                return result
            else:
                return list(reader)
    
    def write_pickle(self, filename: str, data: Any) -> str:
        """
        Write data as pickle to a file in the outputs directory.
        
        Args:
            filename: Name of the file to write to
            data: Data to serialize as pickle
            
        Returns:
            Path to the written file
        """
        full_path = self._get_full_path(filename)
        with open(full_path, 'wb') as f:
            pickle.dump(data, f)
        return str(full_path)
    
    def read_pickle(self, filename: str) -> Any:
        """
        Read pickled data from a file in the outputs directory.
        
        Args:
            filename: Name of the file to read from
            
        Returns:
            Deserialized pickled data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        full_path = self._get_full_path(filename)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        with open(full_path, 'rb') as f:
            return pickle.load(f)
    
    def file_exists(self, filename: str) -> bool:
        """
        Check if a file exists in the outputs directory.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if the file exists, False otherwise
        """
        full_path = self._get_full_path(filename)
        return full_path.exists()
    
    def list_files(self, subdir: str = "", pattern: str = "*") -> List[str]:
        """
        List files in the outputs directory or a subdirectory.
        
        Args:
            subdir: Subdirectory within outputs to list files from
            pattern: Glob pattern to filter files
            
        Returns:
            List of filenames matching the pattern
        """
        dir_path = self.outputs_dir / subdir if subdir else self.outputs_dir
        return [str(p.relative_to(self.outputs_dir)) for p in dir_path.glob(pattern) if p.is_file()]
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from the outputs directory.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if the file was deleted, False if it didn't exist
        """
        full_path = self._get_full_path(filename)
        if full_path.exists():
            full_path.unlink()
            return True
        return False


# Singleton instance for global use
cache = OutputCache() 