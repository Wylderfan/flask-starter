from datetime import datetime
from app import db


class Item(db.Model):
    """Example model — replace or extend with your own domain models."""
    __tablename__ = "items"

    id         = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    profile_id = db.Column(db.String(100), nullable=False)
    name       = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<Item profile={self.profile_id!r} name={self.name!r}>"
