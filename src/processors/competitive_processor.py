"""Processor for competitive analysis datasets."""

import html
import json
import logging
import re
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from .base_processor import BaseProcessor
from ..utils.tech_filter import is_tech_startup, is_tech_industry, is_tech_topic, is_metric_only_dataset

logger = logging.getLogger(__name__)


def is_anonymized_name(name: str) -> bool:
    """Check if a company name appears to be anonymized (e.g., 'Startup_1', 'Company_123')."""
    if not name or not isinstance(name, str):
        return False
    name_lower = name.lower().strip()
    # Check for common anonymization patterns
    patterns = [
        r'^startup_\d+$',
        r'^company_\d+$',
        r'^firm_\d+$',
        r'^entity_\d+$',
        r'^org_\d+$',
    ]
    return any(re.match(pattern, name_lower) for pattern in patterns)


def create_descriptive_identifier(row: pd.Series, company_name: str, df: pd.DataFrame) -> str:
    """Create a more descriptive identifier for anonymized company entries."""
    parts = []
    
    # Add industry if available
    industry_cols = ['Industry', 'industry', 'category', 'Category', 'sector', 'Sector']
    for col in industry_cols:
        if col in df.columns and pd.notna(row[col]):
            parts.append(str(row[col]))
            break
    
    # Add country if available
    country_cols = ['Country', 'country', 'location', 'Location', 'headquarters', 'Headquarters']
    for col in country_cols:
        if col in df.columns and pd.notna(row[col]):
            parts.append(str(row[col]))
            break
    
    # Add tech stack if available
    tech_cols = ['Tech Stack', 'tech_stack', 'technology', 'Technology', 'core_technology', 'Core_Technology']
    for col in tech_cols:
        if col in df.columns and pd.notna(row[col]):
            tech = str(row[col])
            # Take first tech if multiple
            if ',' in tech:
                tech = tech.split(',')[0].strip()
            parts.append(tech)
            break
    
    if parts:
        return f"{company_name} ({', '.join(parts)})"
    return company_name


def is_dataset_mostly_anonymized(df: pd.DataFrame, company_name_col: Optional[str] = None) -> bool:
    """Check if a dataset is mostly anonymized (not useful for competitive analysis)."""
    if company_name_col is None:
        # Try to find company name column
        potential_cols = ['name', 'company_name', 'company', 'startup_name', 'title', 
                          'Startup Name', 'Company Name', 'Company', 'Name', 'Company_Name']
        for col in potential_cols:
            if col in df.columns:
                company_name_col = col
                break
    
    if not company_name_col or company_name_col not in df.columns:
        return False
    
    # Check a sample of company names
    sample_size = min(100, len(df))
    sample_names = df[company_name_col].dropna().head(sample_size)
    
    if len(sample_names) == 0:
        return False
    
    anonymized_count = sum(is_anonymized_name(str(name)) for name in sample_names)
    anonymized_ratio = anonymized_count / len(sample_names)
    
    # If more than 80% are anonymized, consider the dataset mostly anonymized
    return anonymized_ratio > 0.8


class CompetitiveProcessor(BaseProcessor):
    """Process competitive analysis datasets (startups, competitors, funding)."""
    
    def __init__(self, output_dir: Path = Path("data/processed/competitive")):
        super().__init__("competitive", output_dir)
    
    def process_csv_file(
        self, 
        csv_path: Path, 
        output_file: Path,
        text_columns: Optional[list] = None,
        company_name_col: Optional[str] = None
    ) -> int:
        """
        Process a CSV file with startup/competitor data.
        
        Args:
            csv_path: Path to CSV file
            output_file: Output JSONL file
            text_columns: Columns to extract as text (if None, auto-detect)
            company_name_col: Column name for company name
            
        Returns:
            Number of chunks created
        """
        try:
            # Try different encodings for CSV files
            try:
                df = pd.read_csv(csv_path, low_memory=False, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(csv_path, low_memory=False, encoding='latin-1')
                except UnicodeDecodeError:
                    df = pd.read_csv(csv_path, low_memory=False, encoding='cp1252', errors='ignore')
            logger.info(f"Processing {csv_path.name}: {len(df)} rows")
        except Exception as e:
            logger.error(f"Error reading {csv_path}: {e}")
            return 0
        
        # Filter for tech startups only
        original_count = len(df)
        if 'Industry' in df.columns:
            # Filter by Industry column
            df = df[df['Industry'].apply(is_tech_industry)]
            logger.info(f"  Filtered to {len(df)} tech startups (from {original_count} total)")
        elif 'Topic' in df.columns:
            # Filter by Topic column (Product Hunt)
            df = df[df['Topic'].apply(is_tech_topic)]
            logger.info(f"  Filtered to {len(df)} tech products (from {original_count} total)")
        elif 'category_code' in df.columns:
            # Filter by category_code (Crunchbase)
            from ..utils.tech_filter import is_tech_category
            df = df[df['category_code'].apply(is_tech_category)]
            logger.info(f"  Filtered to {len(df)} tech companies (from {original_count} total)")
        else:
            # Use comprehensive tech filter on rows
            df = df[df.apply(is_tech_startup, axis=1)]
            logger.info(f"  Filtered to {len(df)} tech startups (from {original_count} total)")
        
        if len(df) == 0:
            logger.warning(f"  No tech startups found in {csv_path.name} after filtering")
            return 0
        
        # Check if dataset is metric-only (not useful for competitive analysis)
        if is_metric_only_dataset(columns=list(df.columns)):
            logger.warning(f"  Skipping metric-only dataset: {csv_path.name} (contains only metrics/indices without company names or descriptions - not useful for competitive analysis)")
            return 0
        
        # Check if dataset is mostly anonymized (not useful for competitive analysis)
        if is_dataset_mostly_anonymized(df, company_name_col):
            logger.warning(f"  Skipping mostly anonymized dataset: {csv_path.name} (contains anonymized company names like 'Startup_1', 'Startup_2', etc. - not useful for competitive analysis)")
            return 0
        
        # Auto-detect text columns if not provided
        if text_columns is None:
            text_columns = []
            potential_cols = ['description', 'tagline', 'pitch', 'summary', 
                            'overview', 'about', 'one_liner', 'mission']
            for col in potential_cols:
                if col in df.columns:
                    text_columns.append(col)
        
        # Auto-detect company name column
        if company_name_col is None:
            potential_cols = ['name', 'company_name', 'company', 'startup_name', 'title', 
                            'Startup Name', 'Company Name', 'Company', 'Name']
            for col in potential_cols:
                if col in df.columns:
                    company_name_col = col
                    break
        
        chunk_count = 0
        
        for idx, row in df.iterrows():
            # Extract text from multiple columns
            text_parts = []
            for col in text_columns:
                if col in df.columns and pd.notna(row[col]):
                    text_parts.append(str(row[col]))
            
            # If no text columns found, try to create text from all columns
            if not text_parts:
                text_parts = [f"{col}: {row[col]}" for col in df.columns 
                             if pd.notna(row[col]) and col != company_name_col]
            
            combined_text = " | ".join(text_parts)
            combined_text = self.clean_text(combined_text)
            
            if not combined_text or len(combined_text) < 50:
                continue
            
            # Extract company name
            company_name = ""
            if company_name_col and company_name_col in df.columns:
                company_name = str(row[company_name_col]) if pd.notna(row[company_name_col]) else ""
            
            # Check if company name is anonymized
            is_anonymized = is_anonymized_name(company_name) if company_name else False
            
            # For anonymized names, create a more descriptive identifier
            if is_anonymized and company_name:
                descriptive_name = create_descriptive_identifier(row, company_name, df)
                # Prepend descriptive identifier to text for better searchability
                if descriptive_name != company_name:
                    combined_text = f"Company: {descriptive_name} | {combined_text}"
            
            # Create metadata
            metadata = self.extract_metadata(
                csv_path,
                f"{csv_path.stem}_{idx}",
                additional_metadata={
                    "company_name": company_name,
                    "is_anonymized": is_anonymized,
                    "row_index": int(idx),
                    "source_type": "csv"
                }
            )
            
            # Add other relevant columns to metadata
            for col in df.columns:
                if col not in text_columns and col != company_name_col:
                    if pd.notna(row[col]):
                        metadata[col] = str(row[col])
            
            # Save as single chunk (preserve full company context)
            self.save_chunk(combined_text, metadata, output_file)
            chunk_count += 1
        
        return chunk_count
    
    def process_jsonl_file(self, jsonl_path: Path, output_file: Path) -> int:
        """Process a JSONL file."""
        chunk_count = 0
        
        try:
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                # Check first few lines to determine if it's metric-only
                first_lines = []
                for idx, line in enumerate(f):
                    if idx < 5:  # Check first 5 lines
                        try:
                            data = json.loads(line)
                            first_lines.append(data)
                        except json.JSONDecodeError:
                            pass
                    else:
                        break
                
                # Check if dataset is metric-only
                if first_lines and is_metric_only_dataset(data=first_lines[0]):
                    logger.warning(f"  Skipping metric-only dataset: {jsonl_path.name} (contains only metrics/indices without company names or descriptions - not useful for competitive analysis)")
                    return 0
                
                # Reset file pointer and process
                f.seek(0)
                
                # Get file size for progress tracking
                file_size = jsonl_path.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
                
                # Log if file is large
                if file_size_mb > 100:
                    logger.info(f"  Large file detected ({file_size_mb:.1f} MB), processing may take a while...")
                
                log_interval = 50000  # Log every 50k lines
                
                for idx, line in enumerate(f):
                    try:
                        # Progress logging for large files
                        if idx > 0 and idx % log_interval == 0:
                            logger.info(f"  Processed {idx:,} lines...")
                        
                        data = json.loads(line)
                        text = ""
                        
                        # Extract text from common fields
                        if isinstance(data, dict):
                            text_fields = ['text', 'content', 'article', 'story', 'description']
                            for field in text_fields:
                                if field in data:
                                    text = str(data[field])
                                    break
                            
                            # If no text field, convert dict to string
                            if not text:
                                text = json.dumps(data, ensure_ascii=False)
                        else:
                            text = str(data)
                        
                        text = self.clean_text(text)
                        if not text or len(text) < 50:
                            continue
                        
                        # Chunk if too long
                        chunks = self.chunk_text(text, chunk_size=1000, chunk_overlap=200)
                        
                        for chunk_idx, chunk in enumerate(chunks):
                            metadata = self.extract_metadata(
                                jsonl_path,
                                f"{jsonl_path.stem}_{idx}_{chunk_idx}",
                                additional_metadata={
                                    "source_type": "jsonl",
                                    "chunk_index": chunk_idx,
                                    "total_chunks": len(chunks)
                                }
                            )
                            
                            # Preserve original data fields in metadata
                            if isinstance(data, dict):
                                for key, value in data.items():
                                    if key not in ['text', 'content', 'article', 'story', 'description']:
                                        if isinstance(value, (str, int, float, bool)):
                                            metadata[key] = value
                            
                            self.save_chunk(chunk, metadata, output_file)
                            chunk_count += 1
                    
                    except json.JSONDecodeError:
                        logger.warning(f"Skipping invalid JSON line {idx} in {jsonl_path}")
                        continue
        
        except Exception as e:
            logger.error(f"Error processing {jsonl_path}: {e}")
        
        return chunk_count
    
    def process_json_file(self, json_path: Path, output_file: Path) -> int:
        """Process a JSON file."""
        chunk_count = 0
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = [data]
            else:
                logger.warning(f"Unexpected JSON structure in {json_path}")
                return 0
            
            for idx, item in enumerate(items):
                text = ""
                if isinstance(item, dict):
                    text_fields = ['text', 'content', 'description', 'pitch', 'tagline']
                    for field in text_fields:
                        if field in item:
                            text = str(item[field])
                            break
                    
                    if not text:
                        text = json.dumps(item, ensure_ascii=False)
                else:
                    text = str(item)
                
                text = self.clean_text(text)
                if not text or len(text) < 50:
                    continue
                
                chunks = self.chunk_text(text, chunk_size=1000, chunk_overlap=200)
                
                for chunk_idx, chunk in enumerate(chunks):
                    metadata = self.extract_metadata(
                        json_path,
                        f"{json_path.stem}_{idx}_{chunk_idx}",
                        additional_metadata={
                            "source_type": "json",
                            "chunk_index": chunk_idx,
                            "total_chunks": len(chunks)
                        }
                    )
                    
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key not in ['text', 'content', 'description', 'pitch', 'tagline']:
                                if isinstance(value, (str, int, float, bool)):
                                    metadata[key] = value
                    
                    self.save_chunk(chunk, metadata, output_file)
                    chunk_count += 1
        
        except Exception as e:
            logger.error(f"Error processing {json_path}: {e}")
        
        return chunk_count
    
    def process_excel_file(
        self, 
        excel_path: Path, 
        output_file: Path,
        text_columns: Optional[list] = None,
        company_name_col: Optional[str] = None
    ) -> int:
        """
        Process Excel files (XLSX, XLS) with startup/competitor data.
        
        Args:
            excel_path: Path to Excel file
            output_file: Output JSONL file
            text_columns: Columns to extract as text (if None, auto-detect)
            company_name_col: Column name for company name
            
        Returns:
            Number of chunks created
        """
        try:
            # Read first sheet
            df = pd.read_excel(excel_path, sheet_name=0, engine='openpyxl')
            logger.info(f"Processing Excel: {excel_path.name}: {len(df)} rows")
        except Exception as e:
            logger.error(f"Error reading Excel {excel_path}: {e}")
            return 0
        
        # Filter for tech startups only (same logic as CSV)
        original_count = len(df)
        if 'Industry' in df.columns:
            df = df[df['Industry'].apply(is_tech_industry)]
            logger.info(f"  Filtered to {len(df)} tech startups (from {original_count} total)")
        elif 'Topic' in df.columns:
            df = df[df['Topic'].apply(is_tech_topic)]
            logger.info(f"  Filtered to {len(df)} tech products (from {original_count} total)")
        elif 'category_code' in df.columns:
            from ..utils.tech_filter import is_tech_category
            df = df[df['category_code'].apply(is_tech_category)]
            logger.info(f"  Filtered to {len(df)} tech companies (from {original_count} total)")
        else:
            df = df[df.apply(is_tech_startup, axis=1)]
            logger.info(f"  Filtered to {len(df)} tech startups (from {original_count} total)")
        
        if len(df) == 0:
            logger.warning(f"  No tech startups found in {excel_path.name} after filtering")
            return 0
        
        # Check if dataset is metric-only (not useful for competitive analysis)
        if is_metric_only_dataset(columns=list(df.columns)):
            logger.warning(f"  Skipping metric-only dataset: {excel_path.name} (contains only metrics/indices without company names or descriptions - not useful for competitive analysis)")
            return 0
        
        # Check if dataset is mostly anonymized (not useful for competitive analysis)
        if is_dataset_mostly_anonymized(df, company_name_col):
            logger.warning(f"  Skipping mostly anonymized dataset: {excel_path.name} (contains anonymized company names - not useful for competitive analysis)")
            return 0
        
        # Auto-detect text columns if not provided
        if text_columns is None:
            text_columns = []
            potential_cols = ['description', 'tagline', 'pitch', 'summary', 
                            'overview', 'about', 'one_liner', 'mission', 'One_Liner']
            for col in potential_cols:
                if col in df.columns:
                    text_columns.append(col)
        
        # Auto-detect company name column
        if company_name_col is None:
            potential_cols = ['name', 'company_name', 'company', 'startup_name', 'title', 
                            'Company_Name', 'Startup Name', 'Company Name', 'Company', 'Name']
            for col in potential_cols:
                if col in df.columns:
                    company_name_col = col
                    break
        
        chunk_count = 0
        
        for idx, row in df.iterrows():
            # Extract text from multiple columns
            text_parts = []
            for col in text_columns:
                if col in df.columns and pd.notna(row[col]):
                    text_parts.append(str(row[col]))
            
            # If no text columns found, try to create text from all columns
            if not text_parts:
                text_parts = [f"{col}: {row[col]}" for col in df.columns 
                             if pd.notna(row[col]) and col != company_name_col]
            
            combined_text = " | ".join(text_parts)
            combined_text = self.clean_text(combined_text)
            
            if not combined_text or len(combined_text) < 50:
                continue
            
            # Extract company name
            company_name = ""
            if company_name_col and company_name_col in df.columns:
                company_name = str(row[company_name_col]) if pd.notna(row[company_name_col]) else ""
            
            # Check if company name is anonymized
            is_anonymized = is_anonymized_name(company_name) if company_name else False
            
            # For anonymized names, create a more descriptive identifier
            if is_anonymized and company_name:
                descriptive_name = create_descriptive_identifier(row, company_name, df)
                # Prepend descriptive identifier to text for better searchability
                if descriptive_name != company_name:
                    combined_text = f"Company: {descriptive_name} | {combined_text}"
            
            # Create metadata
            metadata = self.extract_metadata(
                excel_path,
                f"{excel_path.stem}_{idx}",
                additional_metadata={
                    "company_name": company_name,
                    "is_anonymized": is_anonymized,
                    "row_index": int(idx),
                    "source_type": "excel"
                }
            )
            
            # Add other relevant columns to metadata
            for col in df.columns:
                if col not in text_columns and col != company_name_col:
                    if pd.notna(row[col]):
                        metadata[col] = str(row[col])
            
            # Save as single chunk (preserve full company context)
            self.save_chunk(combined_text, metadata, output_file)
            chunk_count += 1
        
        return chunk_count
    
    def process_txt_file(self, txt_path: Path, output_file: Path) -> int:
        """Process text files."""
        chunk_count = 0
        
        try:
            with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            content = self.clean_text(content)
            if not content or len(content) < 50:
                return 0
            
            chunks = self.chunk_text(content, chunk_size=1000, chunk_overlap=200)
            
            for chunk_idx, chunk in enumerate(chunks):
                metadata = self.extract_metadata(
                    txt_path,
                    f"{txt_path.stem}_{chunk_idx}",
                    additional_metadata={
                        "source_type": "text_file",
                        "content_type": "article",
                        "file_type": "text",
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks)
                    }
                )
                
                self.save_chunk(chunk, metadata, output_file)
                chunk_count += 1
        
        except Exception as e:
            logger.error(f"Error processing text file {txt_path}: {e}")
        
        return chunk_count
    
    def process_html_file(self, html_path: Path, output_file: Path) -> int:
        """Process HTML files."""
        chunk_count = 0
        
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Basic HTML cleaning (remove tags)
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = html.unescape(content)
            content = self.clean_text(content)
            
            if not content or len(content) < 100:
                return 0
            
            chunks = self.chunk_text(content, chunk_size=1000, chunk_overlap=200)
            
            for chunk_idx, chunk in enumerate(chunks):
                metadata = self.extract_metadata(
                    html_path,
                    f"{html_path.stem}_{chunk_idx}",
                    additional_metadata={
                        "source_type": "html_file",
                        "content_type": "article",
                        "file_type": "html",
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks)
                    }
                )
                
                self.save_chunk(chunk, metadata, output_file)
                chunk_count += 1
        
        except Exception as e:
            logger.error(f"Error processing HTML file {html_path}: {e}")
        
        return chunk_count
    
    def process_dataset(
        self, 
        input_dir: Path,
        output_file: Optional[Path] = None
    ) -> int:
        """
        Process all competitive analysis datasets.
        
        Args:
            input_dir: Directory containing raw competitive data
            output_file: Optional output file path
            
        Returns:
            Total number of chunks created
        """
        if output_file is None:
            output_file = self.output_dir / "competitive_data.jsonl"
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Clear output file if it exists
        if output_file.exists():
            try:
                output_file.unlink()
            except Exception as e:
                logger.warning(f"Could not delete existing file {output_file}: {e}")
        
        total_chunks = 0
        
        # Process CSV files
        for csv_file in input_dir.rglob("*.csv"):
            if csv_file.name.startswith('.'):
                continue
            logger.info(f"Processing CSV: {csv_file}")
            chunks = self.process_csv_file(csv_file, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        # Process JSONL files
        for jsonl_file in input_dir.rglob("*.jsonl"):
            if jsonl_file.name.startswith('.'):
                continue
            logger.info(f"Processing JSONL: {jsonl_file}")
            chunks = self.process_jsonl_file(jsonl_file, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        # Process JSON files
        for json_file in input_dir.rglob("*.json"):
            if json_file.name.startswith('.') or json_file.name == 'package.json':
                continue
            logger.info(f"Processing JSON: {json_file}")
            chunks = self.process_json_file(json_file, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        # Process Excel files (XLSX, XLS)
        for excel_file in input_dir.rglob("*.xlsx"):
            if excel_file.name.startswith('.'):
                continue
            logger.info(f"Processing Excel: {excel_file}")
            chunks = self.process_excel_file(excel_file, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        for excel_file in input_dir.rglob("*.xls"):
            if excel_file.name.startswith('.'):
                continue
            logger.info(f"Processing Excel: {excel_file}")
            chunks = self.process_excel_file(excel_file, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        # Process TXT files
        for txt_file in input_dir.rglob("*.txt"):
            if txt_file.name.startswith('.'):
                continue
            logger.info(f"Processing TXT: {txt_file}")
            chunks = self.process_txt_file(txt_file, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        # Process HTML files
        for html_file in input_dir.rglob("*.html"):
            if html_file.name.startswith('.'):
                continue
            logger.info(f"Processing HTML: {html_file}")
            chunks = self.process_html_file(html_file, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        logger.info(f"Total chunks created: {total_chunks}")
        return total_chunks

