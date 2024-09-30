from .db import db

class viewCustomers(db.Model):
    __tablename__ = 'view_customers'
    id_customer = db.Column(db.Integer, primary_key=True)
    occupation_name = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(500), nullable=False)
    id_customer_type = db.Column(db.Integer, nullable=False)
    type_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.String(50), nullable=False)
    updated_at = db.Column(db.String(50), nullable=False)

    def as_dict(self):
        return {
            "id_customer": self.id_customer,
            "occupation_name": self.occupation_name,
            "customer_name": self.customer_name,
            "id_customer_type": self.id_customer_type,
            "type_name": self.type_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class viewInteractions(db.Model):
    __tablename__ = 'view_interactions'
    id_customer_type = db.Column(db.Integer, primary_key=True)
    channel_counts = db.Column(db.JSON, nullable=True)

    def as_dict(self):
        return {
            "id_customer_type": self.id_customer_type,
            "channel_counts": self.channel_counts
        }

class User(db.Model):
    __tablename__ = 'users'
    id_user = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    permissions = db.Column(db.JSON, default={})

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    permissions = db.Column(db.JSON, default={})
