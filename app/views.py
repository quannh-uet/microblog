from app.forms import EditForm, PostForm
from flask import render_template, flash, redirect, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .models import User, Post
from oauth import OAuthSignIn
from datetime import datetime
from config import POSTS_PER_PAGE


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    user = g.user
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False).items
    return render_template('index.html', title='Home', form=form, user=user, posts=posts)


@app.route('/user/<userid>')
@app.route('/user/<userid>/<int:page>')
@login_required
def user(userid, page=1):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        flash('User %s not found.' % userid)
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False).items
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/follow/<userid>')
@login_required
def follow(userid):
    userid = int(userid)
    user = User.query.filter_by(id=userid).first()
    if user is None:
        flash('User %s not found.' % userid)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', userid=userid))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow %s .' % userid)
        return redirect(url_for('user', userid=userid))
    db.session.add(u)
    db.session.commit()
    flash('You are now following %s !' % userid)
    return redirect(url_for('user', userid=userid))


@app.route('/unfollow/<userid>')
@login_required
def unfollow(userid):
    userid = int(userid)
    user = User.query.filter_by(id=userid).first()
    if user is None:
        flash('User %s not found.' % userid)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', userid=userid))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow %s .' % userid)
        return redirect(url_for('user', userid=userid))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following %s .' % userid)
    return redirect(url_for('user', userid=userid))


@app.route('/detail')
def detail():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your browser is %s</p>' % user_agent


@lm.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not g.user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not g.user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, avatar_url = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(
            social_id=social_id, nickname=username, avatar_url=avatar_url)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
