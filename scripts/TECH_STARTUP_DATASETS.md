# Tech Startup-Specific Datasets Recommendations

## Strategy: Use Tech-Focused Sources + Smart Filtering

Instead of filtering general datasets (which reduces size), use **sources that are already tech-focused** or have tech-specific categories.

---

## 🎯 **Kaggle - Tech Startup Specific Datasets**

### **SaaS / Software Companies:**
- `justinas/startup-investments` ✅ (you have this - mostly tech)
- `vineethakkinapalli/ai-companies` ✅ (you have this - AI tech companies)
- Search: `"SaaS companies"`, `"software startups"`, `"B2B SaaS"`

### **Developer Tools / DevTools:**
- Search: `"developer tools"`, `"DevTools"`, `"programming tools"`
- Product Hunt datasets filtered by "Developer Tools" topic ✅ (you have Product Hunt)

### **API Companies:**
- Search: `"API companies"`, `"API marketplace"`, `"RapidAPI"`
- Product Hunt filtered by "API" topic

### **Cloud Infrastructure:**
- Search: `"cloud infrastructure"`, `"AWS partners"`, `"cloud startups"`
- `"Kubernetes companies"`, `"container startups"`

### **AI/ML Tech Startups:**
- `vineethakkinapalli/ai-companies` ✅ (you have this)
- Search: `"AI startups"`, `"ML companies"`, `"LLM startups"`, `"generative AI companies"`

### **FinTech (Tech-focused):**
- Search: `"fintech startups"`, `"cryptocurrency companies"`, `"blockchain startups"`
- Note: Some FinTech is tech (Stripe, Plaid), some is traditional finance

### **Cybersecurity:**
- Search: `"cybersecurity startups"`, `"security companies"`, `"infosec startups"`

---

## 🌐 **HuggingFace - Tech Startup Datasets**

### **Already Tech-Focused:**
1. **`HackerNoon/where-startups-trend`** ✅ (you have this)
   - Focus: Tech startups with HackerNoon votes (tech community signal)
   - Location: `data/raw/competitive/hackernoon_where_startups_trend/`

2. **`flexonafft/startups-datasets`** ✅ (you have this)
   - Has tech categories: Healthcare Tech, EdTech, etc.
   - Location: `data/raw/competitive/flexonafft_startups_datasets/`

### **Search HuggingFace:**
- Search: `"tech startups"`, `"SaaS"`, `"software companies"`
- URL: https://huggingface.co/datasets?search=tech+startup

---

## 📊 **GitHub - Tech Startup Lists & Datasets**

### **Y Combinator Startups:**
- **Repo**: `ycombinator/yc-startups` (if exists)
- **Alternative**: Search GitHub for `"YC startups" csv` or `"ycombinator companies" json`
- **Manual**: YC has public list at https://www.ycombinator.com/companies

### **Tech Startup Lists:**
- Search: `"awesome startups"`, `"tech companies list"`, `"SaaS directory"`
- Common repos:
  - `lukasz-madon/awesome-remote-job` (remote tech companies)
  - `public-apis/public-apis` (API companies)
  - `toddmotto/public-apis` (API directory)

### **Product Hunt Tech Products:**
- Search: `"product hunt" dataset csv` (filtered by tech topics)
- Your Product Hunt data can be filtered by Topic column

---

## 🔍 **Specialized Tech Startup Sources**

### **1. Crunchbase (via Kaggle/API):**
- **Kaggle**: `arindam235/startup-investments-crunchbase` ✅ (you have this)
- **Filter by**: Industry = "Software", "Internet", "Information Technology"
- **API**: Crunchbase has API (paid) with tech filters

### **2. Product Hunt (Tech-Focused):**
- **Your datasets**: `2020.csv`, `2021.csv`, `2022.csv`, `product_hunt_full.csv` ✅
- **Filter by Topic column**: 
  - "Developer Tools", "API", "SaaS", "Tech", "Web App", "Chrome Extensions"
  - Exclude: "Health & Fitness", "Food", "Fashion", "Consumer"

### **3. AngelList / Wellfound:**
- **GitHub**: Search for `"angellist" dataset` or `"wellfound companies" csv`
- **Note**: Mostly tech startups (platform focus)

### **4. TechCrunch Data:**
- **GitHub**: Search `"techcrunch startups" dataset`
- **RSS**: You can scrape TechCrunch articles (tech-focused)

---

## 🎯 **Recommended Action Plan**

### **Phase 1: Use What You Have (Tech-Filtered)**

1. **Product Hunt** - Filter by tech topics:
   ```python
   tech_topics = ['Developer Tools', 'API', 'SaaS', 'Tech', 'Web App', 
                  'Chrome Extensions', 'Mac', 'Linux', 'Windows']
   ```

2. **AI Companies** - Already tech-focused ✅

3. **HackerNoon Dataset** - Tech community signal ✅

4. **Global Startup Success** - Filter by Industry:
   ```python
   tech_industries = ['AI', 'Tech', 'FinTech', 'EdTech', 'Gaming', 
                     'SaaS', 'Cloud', 'Cybersecurity']
   ```

### **Phase 2: Add Tech-Specific Datasets**

#### **Kaggle (Search & Add):**
```bash
# Search Kaggle for these:
- "SaaS companies dataset"
- "developer tools companies"
- "API marketplace companies"
- "cloud infrastructure startups"
- "cybersecurity companies"
- "DevOps tools"
- "container orchestration companies"
```

#### **HuggingFace (Search & Add):**
- Visit: https://huggingface.co/datasets
- Search: `"tech startup"`, `"SaaS"`, `"software company"`

#### **GitHub (Manual Download):**
- Search: `"tech startups" filename:csv`, `"SaaS companies" filename:json`
- Look for repos with structured lists

---

## 📋 **Specific Dataset Recommendations**

### **High Priority (Tech-Focused):**

1. **YC Companies List** (GitHub/Manual)
   - Source: Y Combinator public list
   - Why: 100% tech startups, high quality
   - Format: Can scrape or find CSV/JSON

2. **Product Hunt - Developer Tools Only** (Filter existing)
   - Your `2020.csv`, `2021.csv`, `2022.csv`
   - Filter: `Topic == "Developer Tools"`

3. **API Directory Datasets** (GitHub)
   - `public-apis/public-apis` repo
   - Lists API companies/services

4. **SaaS Directories** (Various)
   - Search GitHub: `"SaaS directory" csv`
   - Search Kaggle: `"SaaS companies"`

5. **Tech Stack Usage Data** (For competitive analysis)
   - BuiltWith, Wappalyzer datasets (if available)
   - Shows which companies use which tech

### **Medium Priority:**

6. **TechCrunch Startup Database** (Scrape/API)
   - Tech-focused news site
   - Can extract startup mentions

7. **Indie Hackers Directory** (GitHub/Scrape)
   - Tech solo founders / small teams
   - Search: `"indie hackers" dataset`

8. **DevTools Marketplace Lists** (GitHub)
   - VS Code extensions, npm packages (indirect)
   - GitHub topics: `"developer-tools"`, `"saas"`

---

## 🔧 **Implementation: Smart Filtering Script**

Create a filter that:
1. **Keeps tech companies** from mixed datasets
2. **Adds tech-specific datasets** from above sources
3. **Combines** into one tech-only competitive dataset

**Tech Classification Keywords:**
```python
TECH_KEYWORDS = [
    # Product types
    'SaaS', 'API', 'platform', 'software', 'tool', 'framework', 
    'library', 'SDK', 'infrastructure', 'cloud', 'devops',
    # Industries
    'AI', 'ML', 'LLM', 'developer tools', 'DevTools', 
    'cybersecurity', 'fintech', 'edtech', 'healthtech',
    # Technologies
    'Kubernetes', 'Docker', 'microservices', 'serverless',
    'blockchain', 'cryptocurrency', 'API-first'
]

NON_TECH_KEYWORDS = [
    'retail', 'fashion', 'food', 'restaurant', 'consumer goods',
    'real estate', 'hospitality', 'agriculture', 'manufacturing'
]
```

---

## 📊 **Expected Dataset Sizes After Filtering**

- **Unicorn Companies**: ~1,549 → ~800-1,000 (tech only)
- **Global Startup Success**: ~5,000 → ~2,500-3,000 (tech only)
- **Product Hunt**: ~30,000 → ~15,000-20,000 (tech topics)
- **AI Companies**: ~All (already tech)
- **HackerNoon**: ~All (tech community)

**Total Tech Companies**: ~20,000-25,000 (sufficient for RAG)

---

## 🚀 **Next Steps**

1. **Filter existing datasets** using tech keywords
2. **Add tech-specific sources** from above
3. **Create unified tech-only dataset** for RAG
4. **Document filtering logic** for reproducibility

Would you like me to create the filtering script and add tech-specific dataset sources to your config?


