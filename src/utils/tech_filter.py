"""Tech startup filtering utilities - reusable across all processors."""

# Tech industries (from Industry column)
TECH_INDUSTRIES = [
    'AI', 'Artificial Intelligence', 'Machine Learning', 'ML',
    'SaaS', 'Software', 'Software as a Service',
    'Tech', 'Technology', 'Information Technology', 'IT',
    'Cloud', 'Cloud Computing', 'Infrastructure',
    'DevOps', 'Developer Tools', 'DevTools',
    'Cybersecurity', 'Security', 'InfoSec',
    'FinTech', 'Financial Technology',
    'EdTech', 'Education Technology',
    'HealthTech', 'Health Technology',
    'API', 'Platform', 'Framework',
    'Data Science', 'Analytics', 'Big Data',
    'Blockchain', 'Cryptocurrency',
    'Automation', 'Integration',
    'Enterprise Software', 'B2B Software',
    'Mobile App Development', 'Web Development',
    'E-commerce Technology',  # Tech e-commerce platforms, not retail
]

# Non-tech industries to exclude
NON_TECH_INDUSTRIES = [
    'Retail', 'Fashion', 'Food', 'Restaurant', 'FoodTech',  # FoodTech might be tech, but often not
    'Consumer Goods', 'Consumer', 'Lifestyle',
    'Real Estate', 'Hospitality', 'Travel',
    'Agriculture', 'Manufacturing', 'Construction',
    'Entertainment', 'Media', 'Publishing',
    'Healthcare',  # Healthcare services, not HealthTech
    'Energy',  # Energy services, not energy tech
    'Logistics',  # Logistics services, not logistics tech
    'Gaming',  # Consumer gaming, not game dev tools
]

# Tech topics (for Product Hunt Topic column)
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
    'Open Source',
    'Android',
    'iOS',
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
    'TV Shows',
]

# Tech keywords (for description/tagline filtering)
TECH_KEYWORDS = [
    'api', 'saas', 'platform', 'developer', 'devops', 'cloud',
    'infrastructure', 'framework', 'sdk', 'tool', 'software',
    'automation', 'integration', 'analytics', 'database', 'backend',
    'frontend', 'code', 'programming', 'open source', 'b2b',
    'enterprise', 'cybersecurity', 'security', 'ai', 'ml', 'machine learning',
    'artificial intelligence', 'data science', 'big data',
    'blockchain', 'cryptocurrency', 'fintech', 'edtech', 'healthtech',
    'kubernetes', 'docker', 'microservices', 'serverless',
    'api-first', 'devtools', 'developer tools',
]

# Tech category codes (for Crunchbase category_code)
TECH_CATEGORY_CODES = [
    'software', 'web', 'mobile', 'enterprise', 'saas',
    'developer', 'api', 'platform', 'cloud', 'infrastructure',
    'security', 'analytics', 'data', 'ai', 'machine-learning',
    'fintech', 'edtech', 'healthtech', 'devtools',
    'automation', 'integration', 'database', 'backend', 'frontend',
]


def is_tech_industry(industry: str) -> bool:
    """
    Check if an industry is tech-focused.
    
    Args:
        industry: Industry name from dataset
        
    Returns:
        True if tech industry, False otherwise
    """
    if not industry or not isinstance(industry, str):
        return False
    
    industry_lower = industry.strip().lower()
    
    # Check explicit tech industries
    for tech_ind in TECH_INDUSTRIES:
        if tech_ind.lower() in industry_lower or industry_lower in tech_ind.lower():
            return True
    
    # Check explicit non-tech industries
    for non_tech in NON_TECH_INDUSTRIES:
        if non_tech.lower() in industry_lower or industry_lower in non_tech.lower():
            return False
    
    # Check for tech keywords in industry name
    for keyword in TECH_KEYWORDS:
        if keyword in industry_lower:
            return True
    
    return False


def is_tech_topic(topic: str) -> bool:
    """
    Check if a Product Hunt topic is tech-focused.
    
    Args:
        topic: Topic name from Product Hunt
        
    Returns:
        True if tech topic, False otherwise
    """
    if not topic or not isinstance(topic, str):
        return False
    
    topic = topic.strip()
    
    # Check explicit tech topics
    if topic in TECH_TOPICS:
        return True
    
    # Check explicit non-tech topics
    if topic in NON_TECH_TOPICS:
        return False
    
    # Check for tech keywords
    topic_lower = topic.lower()
    for keyword in TECH_KEYWORDS:
        if keyword in topic_lower:
            return True
    
    return False


def is_tech_category(category_code: str) -> bool:
    """
    Check if a category code is tech-focused (for Crunchbase data).
    
    Args:
        category_code: Category code from dataset
        
    Returns:
        True if tech category, False otherwise
    """
    if not category_code or not isinstance(category_code, str):
        return False
    
    category_lower = category_code.strip().lower()
    
    # Check explicit tech categories
    for tech_cat in TECH_CATEGORY_CODES:
        if tech_cat in category_lower or category_lower in tech_cat:
            return True
    
    return False


def is_tech_startup(
    row: dict,
    industry_col: str = 'Industry',
    topic_col: str = 'Topic',
    category_col: str = 'category_code',
    description_cols: list = None,
    tagline_col: str = 'TagLine',
    name_col: str = 'name'
) -> bool:
    """
    Check if a startup/company is tech-focused based on multiple fields.
    
    Args:
        row: Dictionary/Series with company data
        industry_col: Column name for industry
        topic_col: Column name for topic (Product Hunt)
        category_col: Column name for category code (Crunchbase)
        description_cols: List of column names for descriptions
        tagline_col: Column name for tagline
        name_col: Column name for company/product name
        
    Returns:
        True if tech startup, False otherwise
    """
    if description_cols is None:
        description_cols = ['description', 'short_description', 'overview', 'about', 'one_liner']
    
    # Check industry
    if industry_col in row or hasattr(row, industry_col):
        industry = str(row.get(industry_col, '') if isinstance(row, dict) else getattr(row, industry_col, ''))
        if industry and industry != 'nan':
            if is_tech_industry(industry):
                return True
            # If explicitly non-tech, return False early
            industry_lower = industry.lower()
            for non_tech in NON_TECH_INDUSTRIES:
                if non_tech.lower() in industry_lower:
                    return False
    
    # Check topic (Product Hunt)
    if topic_col in row or hasattr(row, topic_col):
        topic = str(row.get(topic_col, '') if isinstance(row, dict) else getattr(row, topic_col, ''))
        if topic and topic != 'nan':
            if is_tech_topic(topic):
                return True
            if topic in NON_TECH_TOPICS:
                return False
    
    # Check category code (Crunchbase)
    if category_col in row or hasattr(row, category_col):
        category = str(row.get(category_col, '') if isinstance(row, dict) else getattr(row, category_col, ''))
        if category and category != 'nan':
            if is_tech_category(category):
                return True
    
    # Check descriptions/taglines for tech keywords
    text_to_check = []
    
    # Add tagline
    if tagline_col in row or hasattr(row, tagline_col):
        tagline = str(row.get(tagline_col, '') if isinstance(row, dict) else getattr(row, tagline_col, ''))
        if tagline and tagline != 'nan':
            text_to_check.append(tagline.lower())
    
    # Add descriptions
    for desc_col in description_cols:
        if desc_col in row or hasattr(row, desc_col):
            desc = str(row.get(desc_col, '') if isinstance(row, dict) else getattr(row, desc_col, ''))
            if desc and desc != 'nan':
                text_to_check.append(desc.lower())
    
    # Check for tech keywords in text
    combined_text = ' '.join(text_to_check)
    for keyword in TECH_KEYWORDS:
        if keyword in combined_text:
            return True
    
    # Check company/product name
    if name_col in row or hasattr(row, name_col):
        name = str(row.get(name_col, '') if isinstance(row, dict) else getattr(row, name_col, ''))
        if name and name != 'nan':
            name_lower = name.lower()
            tech_name_keywords = ['api', 'dev', 'cloud', 'saas', 'tech', 'data', 'code', 'software']
            if any(keyword in name_lower for keyword in tech_name_keywords):
                return True
    
    return False


def is_metric_only_dataset(data: dict = None, columns: list = None) -> bool:
    """
    Check if a dataset contains only metrics/indices without company names or descriptions.
    
    This detects datasets like flexonafft_startups_datasets that only have:
    - Numeric IDs (id, theme_id, category_id)
    - Financial metrics (start_m, end_m, investments_m, etc.)
    - Index scores (tech_idx, market_idx, etc.)
    - No company names, descriptions, or text content
    
    Args:
        data: Dictionary/row of data (for JSONL) or None (for CSV)
        columns: List of column names (for CSV) or None (for JSONL)
        
    Returns:
        True if dataset appears to be metric-only, False otherwise
    """
    # Metric-only field patterns (these indicate metrics, not company info)
    metric_patterns = [
        'id', 'theme_id', 'category_id', 'type_id',
        '_idx', '_index', '_score', '_rating',
        '_m', '_amount', '_value', '_price',
        'start_m', 'end_m', 'investments_m', 'crowdfunding_m',
        'tech_idx', 'market_idx', 'team_idx', 'comp_idx', 
        'social_idx', 'demand_idx', 'financial_idx',
    ]
    
    # Required fields for useful competitive data
    required_text_fields = [
        'name', 'company_name', 'company', 'startup_name', 'title',
        'description', 'text', 'content', 'tagline', 'pitch', 
        'summary', 'overview', 'about', 'one_liner', 'mission',
        'article', 'story', 'news'
    ]
    
    if columns is not None:
        # CSV case: check column names
        columns_lower = [str(col).lower() for col in columns]
        
        # Check if we have any required text fields
        has_text_field = any(
            any(req_field in col_lower for req_field in required_text_fields)
            for col_lower in columns_lower
        )
        
        if has_text_field:
            return False  # Has text fields, not metric-only
        
        # Check if columns are mostly metric patterns
        metric_count = sum(
            1 for col_lower in columns_lower
            if any(pattern in col_lower for pattern in metric_patterns)
        )
        
        # If most columns are metrics and no text fields, it's metric-only
        if metric_count >= len(columns) * 0.6:  # 60% or more are metrics
            return True
        
        # Check if all columns are numeric-like (id, index, score, etc.)
        if len(columns) > 0 and all(
            any(pattern in col_lower for pattern in metric_patterns) or
            col_lower in ['id', 'index', 'score', 'value', 'amount']
            for col_lower in columns_lower
        ):
            return True
    
    elif data is not None:
        # JSONL case: check data structure
        if not isinstance(data, dict):
            return False
        
        keys_lower = [str(k).lower() for k in data.keys()]
        
        # Check if we have any required text fields
        has_text_field = any(
            any(req_field in key_lower for req_field in required_text_fields)
            for key_lower in keys_lower
        )
        
        if has_text_field:
            return False  # Has text fields, not metric-only
        
        # Check if all values are numeric and keys match metric patterns
        all_numeric = all(
            isinstance(v, (int, float)) or 
            (isinstance(v, str) and v.replace('.', '').replace('-', '').isdigit())
            for v in data.values()
        )
        
        metric_key_count = sum(
            1 for key_lower in keys_lower
            if any(pattern in key_lower for pattern in metric_patterns)
        )
        
        # If all values are numeric and most keys are metric patterns, it's metric-only
        if all_numeric and metric_key_count >= len(keys_lower) * 0.6:
            return True
    
    return False


