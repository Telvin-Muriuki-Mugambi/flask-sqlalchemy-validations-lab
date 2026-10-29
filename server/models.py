from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('name')
    def validate_name(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Author name is required.')

        name = value.strip()
        session = db.session
        if any(
            author is not self and author.name == name
            for author in session.new
            if isinstance(author, Author)
        ):
            raise ValueError('Author names must be unique.')

        with session.no_autoflush:
            existing_author = session.query(Author).filter(Author.name == name)
            if self.id is not None:
                existing_author = existing_author.filter(Author.id != self.id)
            if existing_author.first() is not None:
                raise ValueError('Author names must be unique.')

        return name

    @validates('phone_number')
    def validate_phone_number(self, key, value):
        if (
            not isinstance(value, str)
            or len(value) != 10
            or not value.isascii()
            or not value.isdigit()
        ):
            raise ValueError('Author phone numbers must contain exactly ten digits.')
        return value

    def __repr__(self):
        return f'Author(id={self.id}, name={self.name})'


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    category = db.Column(db.String)
    summary = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('title')
    def validate_title(self, key, value):
        clickbait_phrases = ("won't believe", 'secret', 'top', 'guess')
        if not isinstance(value, str) or not any(
            phrase in value.casefold() for phrase in clickbait_phrases
        ):
            raise ValueError(
                'Post titles must contain "Won\'t Believe", "Secret", "Top", or "Guess".'
            )
        return value

    @validates('content')
    def validate_content(self, key, value):
        if not isinstance(value, str) or len(value) < 250:
            raise ValueError('Post content must be at least 250 characters long.')
        return value

    @validates('summary')
    def validate_summary(self, key, value):
        if value is not None and (not isinstance(value, str) or len(value) > 250):
            raise ValueError('Post summaries cannot exceed 250 characters.')
        return value

    @validates('category')
    def validate_category(self, key, value):
        if value not in ('Fiction', 'Non-Fiction'):
            raise ValueError('Post category must be Fiction or Non-Fiction.')
        return value


    def __repr__(self):
        return f'Post(id={self.id}, title={self.title} content={self.content}, summary={self.summary})'
