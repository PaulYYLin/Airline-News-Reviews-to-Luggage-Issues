# Spider Documentation

## Reddit Crawler Documentation

### Overview
---

The `Reddit.py` script is a crawler designed to monitor and collect posts from specified subreddits on Reddit. It uses both RSS feeds for monitoring updates and the Reddit API (via PRAW) for retrieving detailed post information.

### Configuration
---

The crawler is configured using environment variables stored in a `.env` file:

```
REDDIT_CONFIG='{"client_id": "...", "client_secret": "...", "user_agent": "...", "username": "...", "password": "..."}'

REDDIT_SETTINGS='{"listened_subreddits": ["travel"], "max_runs": 5, "monitor_gap_time": 180, "recent_posts_limit": 5}'
```

#### Authentication Parameters (REDDIT_CONFIG)

| Parameter | Description |
|-----------|-------------|
| `client_id` | Reddit API client ID |
| `client_secret` | Reddit API client secret |
| `user_agent` | User agent string for API requests |
| `username` | Reddit account username |
| `password` | Reddit account password |
| `listened_subreddits` | List of subreddits to monitor |

#### Crawler Settings (REDDIT_SETTINGS)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `listened_subreddits` | List of subreddits to monitor | `[]` |
| `max_runs` | Maximum number of monitoring cycles | `5` |
| `monitor_gap_time` | Time between monitoring cycles (seconds) | `180` |
| `recent_posts_limit` | Number of recent posts to retrieve per subreddit | `5` |

### Crawling Process
---

The crawler operates in the following sequence:

1. **Initialization**:
   - Loads configuration from environment variables
   - Authenticates with Reddit API
   - Sets up monitoring parameters

2. **Monitoring Cycle**:
   - Checks RSS feeds of specified subreddits for updates
   - Identifies subreddits with new posts since last check
   - Updates the last check timestamp

3. **Data Collection**:
   - For each updated subreddit, retrieves recent posts using the Reddit API
   - Collects detailed information about each post:
     - Subreddit name
     - Post ID
     - Title
     - Author
     - Creation time (UTC)
     - URL
     - Permalink
     - Post content (selftext)
     - Score
     - Number of comments
     - Post type (self post or link)

4. **Data Storage**:
   - Saves collected post data to JSON files in the `data/` directory
   - Files are named with timestamps (e.g., `reddit_data_20230415_123045.json`)

5. **Cycle Repetition**:
   - Sleeps for the configured gap time
   - Repeats the process until reaching the maximum number of runs

### Error Handling
---

The crawler implements several error handling mechanisms:

- Exponential backoff for rate limiting (HTTP 429 responses)
- Logging of errors with detailed messages
- Graceful recovery from temporary failures
- Timeout handling for network requests

### Usage
---

To run the crawler:

```bash
python Spider/Reddit.py
```

By default, the script will execute a test run that retrieves one post from the "travel" subreddit and prints the result.

To run the full monitoring process, uncomment the following line in the script:

```python
executor.operate(max_runs=5)  # Test run 5 times
```

### Customization
---

The crawler can be customized by modifying the environment variables in the `.env` file:

- Add or remove subreddits in the `listened_subreddits` list
- Adjust the monitoring frequency by changing `monitor_gap_time`
- Increase or decrease the number of posts retrieved with `recent_posts_limit`
- Set the number of monitoring cycles with `max_runs` (or set to `null` for infinite operation)

### Output Format
---

The crawler saves data in JSON format with the following structure:

```json
{
  "post_id": {
    "subreddit": "subreddit_name",
    "id": "post_id",
    "title": "Post Title",
    "author": "username",
    "created_utc": "2023-04-15T12:30:45+00:00",
    "url": "https://www.reddit.com/...",
    "permalink": "/r/subreddit/comments/...",
    "selftext": "Post content...",
    "score": 42,
    "num_comments": 7,
    "is_self": true
  },
  // Additional posts...
}
```

This structured data can be used for further analysis, processing, or integration with other systems.



## FlyerTalk Documentation