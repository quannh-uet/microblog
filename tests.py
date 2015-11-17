__author__ = 'quannh'
# !flask/bin/python
import os
import unittest
from datetime import datetime, timedelta
from config import basedir
from app import app, db
from app.models import User, Post


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_follow(self):
        u1 = User(social_id='facebook$1', nickname='1', avatar_url='pik.vn/123456')
        u2 = User(social_id='facebook$2', nickname='2', avatar_url='pik.vn/123456')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unfollow(u2) is None
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.follow(u2) is None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().nickname == '2'
        assert u2.followers.count() == 1
        assert u2.followers.first().nickname == '1'
        u = u1.unfollow(u2)
        assert u is not None
        db.session.add(u)
        db.session.commit()
        assert not u1.is_following(u2)
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

    def test_follow_posts(self):
        # make four users
        u1 = User(social_id='facebook$3', nickname='3', avatar_url='pik.vn/123456')
        u2 = User(social_id='facebook$4', nickname='4', avatar_url='pik.vn/123456')
        u3 = User(social_id='facebook$5', nickname='5', avatar_url='pik.vn/123456')
        u4 = User(social_id='facebook$6', nickname='6', avatar_url='pik.vn/123456')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        # make four posts
        utcnow = datetime.utcnow()
        p1 = Post(body="post from u1", author=u1, timestamp=utcnow + timedelta(seconds=1))
        p2 = Post(body="post from u2", author=u2, timestamp=utcnow + timedelta(seconds=2))
        p3 = Post(body="post from u3", author=u3, timestamp=utcnow + timedelta(seconds=3))
        p4 = Post(body="post from u4", author=u4, timestamp=utcnow + timedelta(seconds=4))
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.commit()
        # setup the followers
        u1.follow(u1)
        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u2)
        u2.follow(u3)
        u3.follow(u3)
        u3.follow(u4)
        u4.follow(u4)
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()
        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        assert len(f1) == 3
        assert len(f2) == 2
        assert len(f3) == 2
        assert len(f4) == 1
        assert f1 == [p4, p2, p1]
        assert f2 == [p3, p2]
        assert f3 == [p4, p3]
        assert f4 == [p4]


if __name__ == '__main__':
    unittest.main()
