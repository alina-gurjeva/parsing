import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        models.Base.metadata.drop_all(bind=self.engine)
        models.Base.metadata.create_all(bind=self.engine)
        self.maker = sessionmaker(bind=self.engine)

    def _get_or_create(self, session, model, **data):
        instance = session.query(model).filter_by(**data).first()
        if instance:
            return instance
        else:
            instance = model(**data)
            return instance

    def add_comments(self, session, data):
        result = []
        for comment in data:
            author = self._get_or_create(
                session,
                models.Author,
                name=comment["comment"]["user"]["full_name"],
                url=comment["comment"]["user"]["url"],
                id=comment["comment"]["user"]["id"],
            )
            comment_db = self._get_or_create(
                session, models.Comment, **comment["comment"], author=author,
            )
            result.append(comment_db)
            result.extend(self.add_comments(session, comment["comment"]["children"]))
        return result

    def add_post(self, data):
        session = self.maker()
        post = self._get_or_create(session, models.Post, **data["post_data"])
        author = self._get_or_create(session, models.Author, **data["author_data"])
        tags = [self._get_or_create(session, models.Tag, **t) for t in data["tags_data"]]
        try:
            comments = [models.Comment(**comment_params) for comment_params in data["comments_data"]]
        except KeyError:
            comments = []

        post.author = author
        for itm in tags:
            itm.posts.append(post)
        for itm in comments:
            if itm.parent_id:
                itm.parent = session.query(models.Comment).filter_by(id=itm.parent_id).first()
        try:
            session.add(post)
            session.commit()
        except sqlalchemy.exc.IntegrityError as error:
            print(error)
            session.rollback()
        finally:
            session.close()
