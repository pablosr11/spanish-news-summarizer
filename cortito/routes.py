from flask import render_template, flash, redirect, url_for
from flask import request
#from app import app
from app.forms import CommentForm


#delete
from app import app, db
from app.models import Article, Article_NLP, Article_Comments
from datetime import datetime, timedelta
from sqlalchemy import desc


@app.route('/')
@app.route('/index')
def index():

    """ 
        every time the page is loaded, check if the task queue is empty and 
        execute full process. Will always be 1 in queue and 1 executing as
        the the queue doesnt update as fast as people can access the website
        it will wait TIME_SLEEP before closing the job. always make sure job_
        timeout is greater than time_sleep

        !!! move this away from here 
    """
    if not len(app.task_queue):
        job = app.task_queue.enqueue('app.tasks.do_work', job_timeout=app.config['JOB_TIMEOUT'])
        print('job queued', job.id)

    

    #pagination
    p = request.args.get('p', 1, type=int)

    #delete
    last_x_hours = (datetime.now()-timedelta(hours=app.config['HOURS_IN_BOARD']))
    articles = db.session.query(Article, Article_NLP) \
        .filter(Article.last_scrape_date>last_x_hours,
                Article.id==Article_NLP.article_id) \
        .distinct(Article.headline) \
        .order_by(desc(Article_NLP.score * app.config['VALUE_NLP'] + 
                        Article.votes * app.config['VALUE_VOTES'])) \
        .paginate(p, app.config['ARTICLES_PER_PAGE'], False)

    #pagination
    next_url = url_for('index', p=articles.next_num) \
        if articles.has_next else None

    return render_template('index.html', articles=articles.items, next_url=next_url)

@app.route('/preguntas')
def preguntas():
    'FAQ route'
    return render_template('preguntas.html')

@app.route('/item')
@app.route('/item/<post_id>', methods=['GET', 'POST'])
def item(post_id):
    'detail view with load/get/submit form and display comments '

    form = CommentForm()

    article = Article.query.filter(Article.id==post_id).first()

    if form.validate_on_submit():

        com = Article_Comments(text=form.comment.data, article_id=post_id, username=form.user.data)
        db.session.add(com)
        db.session.commit()

        return redirect(url_for('item', post_id=post_id))#    flash('Falta tu comentario en {}'.format(form.comment.data))

    return render_template('item.html', form=form, article=article)


@app.route('/vote/<art_id>', methods=['GET', 'POST'])
def vote(art_id):
    'add votes to database and redirect to detail view for item'

    article = db.session.query(Article).filter(Article.id == int(art_id)).first()
    article.votes += 1
    db.session.commit()
    # if theres problem with database, it will get stopped here

    return redirect(url_for('item', post_id=art_id))

@app.route('/None')
def none():
    'redirect None to main'
    return redirect(redirect_url())

@app.errorhandler(404)
def page_not_found(e):
    'redirect 404 to last page or /index'
    return redirect(redirect_url())

def redirect_url(default='index'):
    return request.args.get('next') or request.referrer or url_for(default)

@app.route('/reply/<comment_id>')
def reply():
    'placeholder for replying to comments in future'
    pass