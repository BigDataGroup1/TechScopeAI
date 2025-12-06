"""Reddit API downloader for startup-related subreddits."""

import logging
import os
import json
from pathlib import Path
from typing import List, Optional, Dict
import time

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

logger = logging.getLogger(__name__)


class RedditDownloader:
    """Download posts and comments from Reddit subreddits."""

    def __init__(self, client_id: Optional[str] = None, 
                 client_secret: Optional[str] = None,
                 user_agent: Optional[str] = None):
        """
        Initialize Reddit downloader.
        
        Args:
            client_id: Reddit API client ID (or from REDDIT_CLIENT_ID env var)
            client_secret: Reddit API client secret (or from REDDIT_CLIENT_SECRET env var)
            user_agent: User agent string (or from REDDIT_USER_AGENT env var)
        """
        if not PRAW_AVAILABLE:
            raise ImportError("praw is required. Install with: pip install praw")
        
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = user_agent or os.getenv("REDDIT_USER_AGENT", "TechScopeAI/1.0")
        
        if not self.client_id or not self.client_secret:
            logger.warning("Reddit credentials not found. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
            self.reddit = None
        else:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )

    def download_subreddit(self, subreddit_name: str, output_path: str, 
                          limit: int = 1000, sort_by: str = "hot") -> bool:
        """
        Download posts from a subreddit.
        
        Args:
            subreddit_name: Name of subreddit (e.g., "startups")
            output_path: Directory to save posts
            limit: Maximum number of posts to download
            sort_by: Sort method ("hot", "new", "top", "rising")
            
        Returns:
            True if successful
        """
        if not self.reddit:
            logger.error("Reddit API not initialized. Check credentials.")
            return False
        
        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading {limit} posts from r/{subreddit_name} (sort: {sort_by})")
            
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get posts based on sort method
            if sort_by == "hot":
                posts = subreddit.hot(limit=limit)
            elif sort_by == "new":
                posts = subreddit.new(limit=limit)
            elif sort_by == "top":
                posts = subreddit.top(limit=limit, time_filter="all")
            elif sort_by == "rising":
                posts = subreddit.rising(limit=limit)
            else:
                posts = subreddit.hot(limit=limit)
            
            posts_data = []
            for idx, post in enumerate(posts):
                if idx >= limit:
                    break
                
                post_data = {
                    "id": post.id,
                    "title": post.title,
                    "selftext": post.selftext,
                    "url": post.url,
                    "author": str(post.author) if post.author else "[deleted]",
                    "score": post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comments": post.num_comments,
                    "created_utc": post.created_utc,
                    "permalink": post.permalink,
                    "subreddit": str(post.subreddit),
                }
                
                # Get top comments (limit to 10 per post)
                post.comments.replace_more(limit=0)
                comments = []
                for comment in post.comments.list()[:10]:
                    if hasattr(comment, 'body'):
                        comments.append({
                            "body": comment.body,
                            "author": str(comment.author) if comment.author else "[deleted]",
                            "score": comment.score,
                            "created_utc": comment.created_utc
                        })
                
                post_data["comments"] = comments
                posts_data.append(post_data)
                
                if (idx + 1) % 100 == 0:
                    logger.info(f"Downloaded {idx + 1} posts...")
                    time.sleep(1)  # Rate limiting
            
            # Save to JSON file
            output_file = output_dir / f"{subreddit_name}_{sort_by}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(posts_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully downloaded {len(posts_data)} posts to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading from r/{subreddit_name}: {e}")
            return False

    def download_multiple_subreddits(self, subreddit_names: List[str], 
                                     output_path: str, limit: int = 1000) -> Dict[str, bool]:
        """
        Download from multiple subreddits.
        
        Args:
            subreddit_names: List of subreddit names
            output_path: Base directory to save data
            limit: Maximum posts per subreddit
            
        Returns:
            Dictionary mapping subreddit names to success status
        """
        results = {}
        for subreddit_name in subreddit_names:
            subreddit_path = str(Path(output_path) / subreddit_name)
            results[subreddit_name] = self.download_subreddit(
                subreddit_name, subreddit_path, limit=limit
            )
            time.sleep(2)  # Rate limiting between subreddits
        
        return results

