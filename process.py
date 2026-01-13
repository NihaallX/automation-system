#!/usr/bin/env python3
"""
File Processing Automation System

Simple CLI tool to process files and generate statistics.
Usage: python process.py [options]
"""

import os
import sys
import logging
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """System configuration and constants."""
    
    # Default paths
    DEFAULT_INPUT = "input"
    DEFAULT_OUTPUT = "output"
    
    # Output filenames
    SUMMARY_FILE = "summary.json"
    LOG_FILE = "processing.log"
    
    # Validation rules
    MIN_FILES_REQUIRED = 1
    MAX_FILE_SIZE_MB = 100
    
    # Display settings
    BANNER_WIDTH = 60


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


# ============================================================================
# FILE PROCESSOR
# ============================================================================

class FileProcessor:
    """Main file processing system with validation and safe failure handling."""
    
    def __init__(self, input_folder: str, output_folder: str, verbose: bool = False):
        """
        Initialize the file processor.
        
        Args:
            input_folder: Path to input folder
            output_folder: Path to output folder
            verbose: Show detailed progress messages
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.verbose = verbose
        self.logger = None
        self.start_time = datetime.now()
        
    def setup_logging(self) -> None:
        """Configure logging system."""
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        log_file = self.output_folder / Config.LOG_FILE
        
        self.logger = logging.getLogger('FileProcessor')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # File handler - detailed logs
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self._print_banner("FILE PROCESSING SYSTEM")
        self.logger.info(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self._print_separator()
        
    def _print_banner(self, text: str) -> None:
        """Print a formatted banner."""
        self.logger.info("=" * Config.BANNER_WIDTH)
        self.logger.info(f"{text:^{Config.BANNER_WIDTH}}")
        self.logger.info("=" * Config.BANNER_WIDTH)
        
    def _print_separator(self) -> None:
        """Print a separator line."""
        self.logger.info("-" * Config.BANNER_WIDTH)
        
    def validate_inputs(self) -> None:
        """Validate that required inputs exist and are valid."""
        self.logger.info("🔍 Validating inputs...")
        self.logger.info("")
        
        # Check 1: Input folder exists
        if not self.input_folder.exists():
            raise ValidationError(
                f"Input folder not found: {self.input_folder.absolute()}"
            )
        self.logger.info(f"  ✓ Input folder exists")
        
        # Check 2: Input folder is a directory
        if not self.input_folder.is_dir():
            raise ValidationError(
                f"Path is not a directory: {self.input_folder.absolute()}"
            )
        self.logger.info(f"  ✓ Path is a directory")
        
        # Check 3: Input folder is readable
        if not os.access(self.input_folder, os.R_OK):
            raise ValidationError(
                f"Cannot read folder: {self.input_folder.absolute()}"
            )
        self.logger.info(f"  ✓ Folder is readable")
        
        # Check 4: Input folder contains files
        all_items = list(self.input_folder.iterdir())
        files = [item for item in all_items if item.is_file()]
        folders = [item for item in all_items if item.is_dir()]
        
        if len(files) < Config.MIN_FILES_REQUIRED:
            error_parts = [
                f"Input folder must contain at least {Config.MIN_FILES_REQUIRED} file(s).",
                f"Found: {len(files)} file(s)"
            ]
            
            # Provide helpful context about what was found
            if folders:
                folder_names = [f.name for f in folders[:5]]  # Show first 5 folders
                if len(folders) > 5:
                    folder_names.append(f"... and {len(folders) - 5} more")
                error_parts.append(f"Found {len(folders)} subfolder(s): {', '.join(folder_names)}")
                error_parts.append("\nNote: The system only processes files in the root input folder.")
                error_parts.append("Files inside subfolders are NOT processed.")
                error_parts.append("\nSuggestion: Move files from subfolders to the input folder root,")
                error_parts.append(f"or run the script directly on the subfolder: python process.py -i \"{folders[0].absolute()}\"")
            elif len(all_items) == 0:
                error_parts.append("The folder is completely empty.")
            
            self.logger.debug(f"Contents of input folder: {[item.name for item in all_items]}")
            raise ValidationError("\n".join(error_parts))
        
        self.logger.info(f"  ✓ Found {len(files)} file(s)")
        if folders:
            self.logger.debug(f"  ℹ Also found {len(folders)} subfolder(s) (will be ignored)")
        
        # Check 5: Files are readable
        unreadable = [f.name for f in files if not os.access(f, os.R_OK)]
        if unreadable:
            raise ValidationError(
                f"Cannot read files: {', '.join(unreadable)}"
            )
        self.logger.info(f"  ✓ All files are readable")
        
        self.logger.info("")
        self.logger.info(f"✅ Validation passed - {len(files)} file(s) ready")
        self._print_separator()
        
    def count_lines(self, file_path: Path) -> Optional[int]:
        """Count lines in a text file."""
        try:
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return sum(1 for _ in f)
                except UnicodeDecodeError:
                    continue
            return None
        except Exception as e:
            self.logger.debug(f"Could not count lines in {file_path.name}: {e}")
            return None
    
    def process_files(self) -> Dict:
        """Process all files and gather statistics."""
        self.logger.info("📊 Processing files...")
        self.logger.info("")
        
        files = sorted([item for item in self.input_folder.iterdir() if item.is_file()])
        
        file_stats = []
        total_size = 0
        total_lines = 0
        text_files = 0
        binary_files = 0
        
        for idx, file_path in enumerate(files, 1):
            # Progress indicator
            prefix = f"  [{idx}/{len(files)}]"
            self.logger.info(f"{prefix} {file_path.name}")
            
            # Get file size
            file_size = file_path.stat().st_size
            total_size += file_size
            
            # Count lines if text file
            line_count = self.count_lines(file_path)
            
            if line_count is not None:
                total_lines += line_count
                text_files += 1
                file_type = "text"
                if self.verbose:
                    self.logger.debug(f"        Type: text, Lines: {line_count}, Size: {file_size / 1024:.2f} KB")
            else:
                binary_files += 1
                file_type = "binary"
                if self.verbose:
                    self.logger.debug(f"        Type: binary, Size: {file_size / 1024:.2f} KB")
            
            # Check for large files
            size_mb = file_size / (1024 * 1024)
            if size_mb > Config.MAX_FILE_SIZE_MB:
                self.logger.warning(f"        ⚠️  Large file: {size_mb:.2f} MB")
            
            # Collect file statistics
            file_info = {
                "name": file_path.name,
                "size_bytes": file_size,
                "size_kb": round(file_size / 1024, 2),
                "type": file_type,
                "line_count": line_count,
                "modified": datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            file_stats.append(file_info)
        
        self.logger.info("")
        self.logger.info(f"✅ Processed {len(files)} file(s) successfully")
        self._print_separator()
        
        # Compile summary
        summary = {
            "processing_info": {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "input_folder": str(self.input_folder.absolute()),
                "output_folder": str(self.output_folder.absolute())
            },
            "statistics": {
                "total_files": len(files),
                "text_files": text_files,
                "binary_files": binary_files,
                "total_size_bytes": total_size,
                "total_size_kb": round(total_size / 1024, 2),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_lines": total_lines
            },
            "files": file_stats
        }
        
        return summary
    
    def write_summary(self, summary: Dict) -> None:
        """Write the summary to a JSON file."""
        summary_path = self.output_folder / Config.SUMMARY_FILE
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            self.logger.info("📝 Output files created:")
            self.logger.info(f"  • Summary: {Config.SUMMARY_FILE}")
            self.logger.info(f"  • Log:     {Config.LOG_FILE}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to write summary: {e}")
    
    def print_summary_stats(self, summary: Dict) -> None:
        """Print summary statistics to console."""
        stats = summary['statistics']
        
        self._print_separator()
        self.logger.info("📈 SUMMARY STATISTICS")
        self.logger.info("")
        self.logger.info(f"  Total Files:   {stats['total_files']}")
        self.logger.info(f"  Text Files:    {stats['text_files']}")
        self.logger.info(f"  Binary Files:  {stats['binary_files']}")
        self.logger.info(f"  Total Size:    {stats['total_size_kb']:.2f} KB ({stats['total_size_mb']:.2f} MB)")
        if stats['total_lines'] > 0:
            self.logger.info(f"  Total Lines:   {stats['total_lines']:,}")
        self._print_separator()
    
    def run(self) -> int:
        """Main execution method."""
        try:
            # Setup
            self.setup_logging()
            
            self.logger.info(f"📂 Input:  {self.input_folder.absolute()}")
            self.logger.info(f"📂 Output: {self.output_folder.absolute()}")
            self._print_separator()
            
            # Validate
            self.validate_inputs()
            
            # Process
            summary = self.process_files()
            
            # Write output
            self.write_summary(summary)
            
            # Show summary
            self.print_summary_stats(summary)
            
            # Success
            duration = (datetime.now() - self.start_time).total_seconds()
            self._print_banner("COMPLETED SUCCESSFULLY")
            self.logger.info(f"Duration: {duration:.2f} seconds")
            self.logger.info(f"Output:   {self.output_folder.absolute()}")
            self._print_banner("")
            
            return 0
            
        except ValidationError as e:
            # Validation failure
            if self.logger:
                self.logger.error("")
                self._print_banner("VALIDATION FAILED")
                self.logger.error(f"❌ {str(e)}")
                self._print_banner("")
                self.logger.error("Please fix the issues and try again.")
            else:
                print(f"ERROR: {str(e)}", file=sys.stderr)
            return 1
            
        except Exception as e:
            # Unexpected error
            if self.logger:
                self.logger.error("")
                self._print_banner("UNEXPECTED ERROR")
                self.logger.error(f"❌ {type(e).__name__}: {str(e)}")
                self._print_banner("")
                self.logger.exception("Full traceback:")
            else:
                print(f"FATAL ERROR: {str(e)}", file=sys.stderr)
            return 2


# ============================================================================
# CLI INTERFACE
# ============================================================================

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Process files and generate statistics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process.py
  python process.py -i my_files
  python process.py -i data -o results
  python process.py --verbose
  python process.py -i C:\\Users\\Documents -o D:\\Output

Exit codes:
  0 = Success
  1 = Validation error
  2 = Unexpected error
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        default=Config.DEFAULT_INPUT,
        help=f'Input folder path (default: {Config.DEFAULT_INPUT})'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=Config.DEFAULT_OUTPUT,
        help=f'Output folder path (default: {Config.DEFAULT_OUTPUT})'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed processing information'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='File Processor 1.0.0'
    )
    
    return parser.parse_args()


def main():
    """Entry point for the file processor."""
    args = parse_arguments()
    
    processor = FileProcessor(
        input_folder=args.input,
        output_folder=args.output,
        verbose=args.verbose
    )
    
    exit_code = processor.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
