from datetime import datetime
from . import db


class CampusItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(40), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(
        db.String(200),
        nullable=False,
        default='Campus database'
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(
        db.String(200),
        nullable=False,
        default='New conversation'
    )
    category = db.Column(
        db.String(40),
        default='general'
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    messages = db.relationship(
        'Message',
        backref='conversation',
        cascade='all, delete-orphan',
        order_by='Message.created_at'
    )


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey('conversation.id'),
        nullable=False
    )
    role = db.Column(
        db.String(20),
        nullable=False
    )
    content = db.Column(
        db.Text,
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    source = db.Column(
        db.String(200)
    )


class Feedback(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    message_id = db.Column(
        db.Integer,
        db.ForeignKey('message.id'),
        nullable=False
    )

    rating = db.Column(
        db.String(20),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    message = db.relationship(
        'Message',
        backref=db.backref(
            'feedback',
            uselist=False
        )
    )


class Admin(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )