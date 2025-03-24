import praw
import os
from dotenv import load_dotenv
import json
import logging
from datetime import datetime, timezone
import pandas as pd
import time


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
REDDIT_CONFIG= json.loads(os.getenv("REDDIT_CONFIG"))


class Reddit:
    def __init__(self):
        """Initialize Reddit client and monitoring parameters"""
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CONFIG["client_id"],
                client_secret=REDDIT_CONFIG["client_secret"],
                user_agent=REDDIT_CONFIG["user_agent"],
                username=REDDIT_CONFIG["username"],
                password=REDDIT_CONFIG["password"]
            )
            user = self.reddit.user.me()
            logger.info(f"Connected to Reddit as: {user}")
        except Exception as e:
            logger.error(f"Failed to connect to Reddit: {e}")
            raise
        
        self.QUERY = REDDIT_CONFIG.get("query", "luggage mishandled")

    
    def get_historical_posts(self, subreddit_name='all', limit=1000, sort='new') -> pd.DataFrame:
        """Get historical posts from a specified subreddit using Reddit API
        Args:
            subreddit_name (str): Name of the subreddit to get posts from ["travel","flight","flying","travelhacks","airtravel"]
            limit (int, optional): Number of posts to retrieve. Defaults to 1000.
        Returns:
            pd.DataFrame: DataFrame containing filtered post data
        """
        start_time = time.time()
        logger.info(f"Attempting to get historical posts from r/{subreddit_name}, limit={limit}")
        
        try:
            subreddit_name = subreddit_name or "all"
            subreddit = self.reddit.subreddit(subreddit_name)
            posts_data = []
            posts_seen = set()
            
            LUGGAGE_KEYWORDS = ["luggage", "bag", "lost", "delayed", "misplaced", "misrouted", "mishandled"]
            
            remaining = limit
            after = None
            
            while remaining > 0:
                batch_size = min(remaining, 1000)
                if sort == 'new':
                    posts = subreddit.new(
                        limit=batch_size, 
                        params={"after": after} if after else None
                    )
                elif sort == 'top':
                    posts = subreddit.top(
                        limit=batch_size, 
                        params={"after": after} if after else None
                    )
                elif sort == 'hot':
                    posts = subreddit.hot(
                        limit=batch_size, 
                        params={"after": after} if after else None
                    )
                
                last_post = None
                batch_count = 0
                
                for post in posts:
                    if post.id in posts_seen:
                        continue
                    
                    posts_seen.add(post.id)
                    batch_count += 1
                    
                    title_lower = post.title.lower()
                    if (any(keyword in title_lower for keyword in LUGGAGE_KEYWORDS) or any(keyword in post.selftext.lower() for keyword in LUGGAGE_KEYWORDS)) and post.selftext is not None:
                        posts_data.append(self._extract_post_data(post))
                    
                    last_post = post
                
                if not last_post or batch_count == 0:
                    break  # No more posts to fetch
                    
                after = f't3_{last_post.id}'
                remaining -= batch_count
                logger.info(f"Fetched batch of {batch_count} posts, {len(posts_data)} matched filters, {remaining} remaining")

            if not posts_data:
                logger.warning(f"No posts found matching criteria for r/{subreddit_name}")
                return pd.DataFrame()
            
            posts_df = pd.DataFrame(posts_data)
            elapsed_time = time.time() - start_time
            logger.info(f"Successfully retrieved {len(posts_data)} posts in {elapsed_time:.2f}s")
            logger.info(f"DataFrame shape={posts_df.shape}, columns={posts_df.columns.tolist()}")
            return posts_df
            
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {str(e)}", exc_info=True)
            return pd.DataFrame()


    def get_posts_from_subreddit(self, subreddit_name='all', limit=5, time_filter='month', sort='new') -> pd.DataFrame:
        """Get posts from a specified subreddit using Reddit API
        Args:
            subreddit_name (str): Name of the subreddit to get posts from
            limit (int, optional): Number of posts to retrieve. Defaults to 5.
            time_filter (str, optional): Time filter for posts. Defaults to 'month'.
            sort (str, optional): Sort order for posts. Defaults to 'new'.
        Returns:
            pd.DataFrame: DataFrame containing post data with Primary Key as post_id
        """
        start_time = time.time()
        logger.info(f"Attempting to get posts from r/{subreddit_name}, params: limit={limit}, time_filter={time_filter}, sort={sort}")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts_data = []
            
            # Simple case for small limits
            posts = subreddit.search(query=self.QUERY, sort=sort, limit=limit, time_filter=time_filter)
            for post in posts:
                if post.selftext is not None:
                    posts_data.append(self._extract_post_data(post))

            # Create and return DataFrame
            if not posts_data:
                logger.warning(f"No posts found matching criteria for r/{subreddit_name}")
                return pd.DataFrame()
            
            posts_df = pd.DataFrame(posts_data)
            elapsed_time = time.time() - start_time
            logger.info(f"Successfully retrieved {len(posts_data)} posts in {elapsed_time:.2f}s")
            logger.info(f"DataFrame shape={posts_df.shape}, columns={posts_df.columns.tolist()}")
            return posts_df
            
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {str(e)}", exc_info=True)
            return pd.DataFrame()

    def _extract_post_data(self, post):
        """Extract relevant data from a post object
        Args:
            post: Reddit post object
        Returns:
            dict: Dictionary containing post data
        """
        return {
            'post_id': str('reddit_' + post.id),
            'subreddit': str(post.subreddit),
            'title': str(post.title),
            'created_utc': pd.to_datetime(datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat()),
            'selftext': str(post.selftext),
            'score': int(post.score),
            'num_comments': int(post.num_comments),
        }




if __name__ == "__main__":
    reddit = Reddit()
    posts_data = reddit.get_posts_from_subreddit(subreddit_name="all", limit=100, time_filter="month", sort="new")
    print(posts_data)