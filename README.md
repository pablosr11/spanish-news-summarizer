# spanish-news-summarizer

Canary Islands' News listing ranked daily by its contents.

- Scrapes top news outlets for newest articles
- Ranks them using TFIDF scores
- Automatic extraction of summaries, top words and topics from each article
- Deployed on Amazon's Elastic Compute Cloud using Nginx, Gunicorn and Redis
- Backend built with Flask and SQLAlchemy using SQLite

