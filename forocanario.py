from app import app, db
from app.models import Article, Words, Article_NLP, Article_Comments

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Article': Article, 'Words': Words,
    'Article_Comments':Article_Comments, 'Article_NLP': Article_NLP}
