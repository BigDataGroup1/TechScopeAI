"""Extract tech startup taglines from Product Hunt data for Marketing agent RAG."""

import pandas as pd
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tech topics to keep (from Product Hunt Topic column)
TECH_TOPICS = [
    'Developer Tools',
    'API',
    'SaaS',
    'Tech',
    'Web App',
    'Chrome Extensions',
    'Mac',
    'Linux',
    'Windows',
    'Productivity',
    'Design Tools',
    'Developer',
    'Software',
    'Platform',
    'Framework',
    'Infrastructure',
    'Cloud',
    'DevOps',
    'Security',
    'Analytics',
    'Database',
    'Backend',
    'Frontend',
    'Mobile App',  # Tech mobile apps, not consumer
    'Integration',
    'Automation',
    'AI',
    'Machine Learning',
    'Data Science',
    'Blockchain',
    'Cryptocurrency',
    'FinTech',
    'EdTech',
    'HealthTech',
    'Enterprise',
    'B2B',
    'Developer API',
    'Code',
    'Programming',
    'Open Source'
]

# Non-tech topics to exclude
NON_TECH_TOPICS = [
    'Health & Fitness',
    'Food',
    'Fashion',
    'Consumer',
    'Lifestyle',
    'Entertainment',
    'Music',
    'Video',
    'Gaming',  # Consumer gaming, not game dev tools
    'Sports',
    'Travel',
    'Shopping',
    'Beauty',
    'Home',
    'Kids',
    'Pets',
    'Photography',  # Consumer photography apps
    'Social Media',  # Consumer social, not B2B
    'Dating',
    'News',
    'Education',  # Consumer education, not EdTech tools
    'Books',
    'Movies',
    'TV Shows'
]


def is_tech_product(row):
    """Check if a product is tech-focused based on Topic and TagLine."""
    topic = str(row.get('Topic', '')).strip()
    tagline = str(row.get('TagLine', '')).strip().lower()
    product_name = str(row.get('ProductName', '')).strip().lower()
    
    # Check topic
    if topic in TECH_TOPICS:
        return True
    if topic in NON_TECH_TOPICS:
        return False
    
    # Check tagline for tech keywords
    tech_keywords = [
        'api', 'saas', 'platform', 'developer', 'devops', 'cloud',
        'infrastructure', 'framework', 'sdk', 'tool', 'software',
        'automation', 'integration', 'analytics', 'database', 'backend',
        'frontend', 'code', 'programming', 'open source', 'b2b',
        'enterprise', 'cybersecurity', 'security', 'ai', 'ml', 'machine learning'
    ]
    
    if any(keyword in tagline for keyword in tech_keywords):
        return True
    
    # Check product name for tech indicators
    tech_name_keywords = ['api', 'dev', 'cloud', 'saas', 'tech', 'data', 'code']
    if any(keyword in product_name for keyword in tech_name_keywords):
        return True
    
    return False


def extract_taglines_from_file(file_path):
    """Extract tech taglines from a Product Hunt CSV file."""
    try:
        logger.info(f"Processing {file_path.name}...")
        df = pd.read_csv(file_path)
        
        # Filter for tech products
        tech_df = df[df.apply(is_tech_product, axis=1)]
        
        # Extract taglines
        taglines = []
        for idx, row in tech_df.iterrows():
            tagline = str(row.get('TagLine', '')).strip()
            product_name = str(row.get('ProductName', '')).strip()
            topic = str(row.get('Topic', '')).strip()
            
            if tagline and tagline != 'nan' and len(tagline) > 10:
                taglines.append({
                    'tagline': tagline,
                    'product_name': product_name,
                    'topic': topic,
                    'source': file_path.name,
                    'upvotes': row.get('Upvotes', 0)
                })
        
        logger.info(f"  Extracted {len(taglines)} tech taglines from {len(df)} total products")
        return taglines
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return []


def main():
    """Extract all tech taglines from Product Hunt datasets."""
    # Input directory
    input_dir = Path("data/raw/competitive")
    
    # Output directory
    output_dir = Path("data/raw/marketing/producthunt_taglines")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all Product Hunt CSV files
    ph_files = [
        input_dir / "2020.csv",
        input_dir / "2021.csv",
        input_dir / "2022.csv",
        input_dir / "product_hunt_full.csv"
    ]
    
    # Filter to only existing files
    ph_files = [f for f in ph_files if f.exists()]
    
    if not ph_files:
        logger.error("No Product Hunt CSV files found!")
        return
    
    logger.info(f"Found {len(ph_files)} Product Hunt files to process")
    logger.info("=" * 60)
    
    # Extract taglines from all files
    all_taglines = []
    for ph_file in ph_files:
        taglines = extract_taglines_from_file(ph_file)
        all_taglines.extend(taglines)
    
    logger.info("=" * 60)
    logger.info(f"Total tech taglines extracted: {len(all_taglines)}")
    
    if not all_taglines:
        logger.warning("No taglines extracted!")
        return
    
    # Remove duplicates (same tagline)
    seen = set()
    unique_taglines = []
    for item in all_taglines:
        tagline_lower = item['tagline'].lower()
        if tagline_lower not in seen:
            seen.add(tagline_lower)
            unique_taglines.append(item)
    
    logger.info(f"Unique taglines: {len(unique_taglines)}")
    
    # Save as JSONL (for RAG)
    jsonl_path = output_dir / "tech_startup_taglines.jsonl"
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for item in unique_taglines:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    logger.info(f"Saved to: {jsonl_path}")
    
    # Also save as CSV for easy viewing
    csv_path = output_dir / "tech_startup_taglines.csv"
    df = pd.DataFrame(unique_taglines)
    df.to_csv(csv_path, index=False, encoding='utf-8')
    logger.info(f"Saved to: {csv_path}")
    
    # Statistics
    logger.info("\n" + "=" * 60)
    logger.info("STATISTICS")
    logger.info("=" * 60)
    logger.info(f"Total taglines: {len(unique_taglines)}")
    logger.info(f"File size: {jsonl_path.stat().st_size / (1024*1024):.2f} MB")
    
    # Top topics
    if 'topic' in df.columns:
        logger.info("\nTop topics:")
        for topic, count in df['topic'].value_counts().head(10).items():
            logger.info(f"  {topic}: {count}")
    
    logger.info("\n✅ Done! Taglines ready for Marketing agent RAG.")


if __name__ == "__main__":
    main()


