from .database import db
from datetime import datetime

class Analysis(db.Model):
    __tablename__ = 'analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    music_id = db.Column(db.Integer, db.ForeignKey('music.id'), nullable=False)
    tempo = db.Column(db.Float)
    key = db.Column(db.String(10))
    energy = db.Column(db.Float)
    danceability = db.Column(db.Float)
    valence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'music_id': self.music_id,
            'tempo': self.tempo,
            'key': self.key,
            'energy': self.energy,
            'danceability': self.danceability,
            'valence': self.valence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }