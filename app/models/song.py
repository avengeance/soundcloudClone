from .db import db, environment, SCHEMA, add_prefix_for_prod
from datetime import datetime

class Song(db.Model):

    __tablename__ = 'songs'

    if environment == 'production':
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    name = db.Column(db.String(50))
    artists = db.Column(db.String(100))
    genre = db.Column(db.String(20))
    description = db.Column(db.String(255))
    audio_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User', back_populates='songs')
    comments = db.relationship('Comment', back_populates='songs', cascade='all, delete-orphan')
    song_likes = db.relationship('SongLike', back_populates='songs', cascade='all, delete-orphan')
    song_images = db.relationship('SongImage', back_populates='songs', cascade='all, delete')
    playlist_songs = db.relationship('PlaylistSong', cascade='all, delete')

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'name': self.name,
            'artists': self.artists,
            'genre': self.genre,
            'description': self.description,
            'audioUrl': self.audio_url,
            'imgUrl': [img.to_dict() for img in self.song_images],
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }
