# Snippets Display Update

## What Changed

### 1. Agents Now Include Snippets in Sources

All agents now include snippet text when adding web search results to sources:

**Before:**
```python
all_sources.append({
    'source': web_result.get('url', 'Web Search'),
    'title': web_result.get('title', ''),
    'similarity': web_result.get('relevance_score', 0)
})
```

**After:**
```python
all_sources.append({
    'source': web_result.get('url', 'Web Search'),
    'title': web_result.get('title', ''),
    'snippet': web_result.get('snippet', ''),  # NEW
    'similarity': web_result.get('relevance_score', 0),
    'is_web_search': True  # NEW - flag to identify web sources
})
```

### 2. Streamlit UI Now Shows Snippets

The Sources section in Streamlit now displays:
- **Title** (clickable link for web sources)
- **Snippet** (first 200 characters of the page content)
- **URL** (clickable "View full article" link)
- **Source type** (Cloud SQL or Web Search)
- **Similarity score**

## Updated Agents

All agents now include snippets:
- ✅ CompetitiveAgent
- ✅ PitchAgent
- ✅ MarketingAgent
- ✅ PatentAgent
- ✅ PolicyAgent
- ✅ TeamAgent

## How It Looks Now

### For Web Search Sources:
```
📚 Sources (Cloud SQL + Web Search)

1. Top Startup Funding Rounds This Week
   This week saw several major funding rounds including...
   🔗 View full article
   Similarity: 0.850 | Web Search
```

### For Cloud SQL Sources:
```
📚 Sources (from Cloud SQL)

1. Competitor Analysis Dataset
   Similarity: 0.600 | Cloud SQL Collection
```

## Benefits

1. **See snippet content** - Know what each source is about without clicking
2. **Clickable titles** - Titles link directly to the article
3. **Clear source type** - Know if it's from Cloud SQL or Web Search
4. **Better context** - Understand which snippet [3] refers to

## Example

When you ask "What startup funding rounds happened in the last week?", you'll now see:

```
📚 Sources (Cloud SQL + Web Search)

1. Top Startup Funding Rounds This Week
   This week saw several major funding rounds including AI companies...
   🔗 View full article
   Similarity: 0.850 | Web Search

2. Latest VC Funding News
   Recent investments in fintech and SaaS startups...
   🔗 View full article
   Similarity: 0.750 | Web Search
```

Now you can see exactly what snippet [1], [2], [3] contain, and click the links to read the full articles!

