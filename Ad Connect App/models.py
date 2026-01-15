from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric
from decimal import Decimal

db=SQLAlchemy()

class Admin(db.Model):
    admin_id = db.Column(db.String, primary_key=True, nullable=False)
    admin_pass = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "admin_id": self.admin_id,
            "admin_pass": self.admin_pass,
        }


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_role = db.Column(db.String, nullable=False) #sponsor/influencer
    user_name = db.Column(db.String, nullable=False)
    user_pass = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    followers = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    earnings = db.Column(Numeric(20, 2), nullable=True)
    category = db.Column(db.String, nullable=True)
    approved = db.Column(db.String, nullable=True)  # approved/flagged
    email = db.Column(db.String, nullable=True)
    children1 = db.relationship("Ad_request", back_populates="parent2", cascade="all, delete-orphan")
    children2 = db.relationship("Campaign", back_populates="parent1", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_role": self.user_role,
            "user_name": self.user_name,
            "description": self.description,
            "followers": self.followers,
            "rating": self.rating,
            "earnings": str(self.earnings) if self.earnings is not None else None,
            "category": self.category,
            "approved": self.approved,
            "email" : self.email,
        }


class Campaign(db.Model):
    campaign_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    budget = db.Column(db.String, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
    visibility = db.Column(db.String, nullable=True)
    approved = db.Column(db.String, nullable=True)  # approved/flagged
    status = db.Column(db.String, nullable=False)  # Active/Inactive

    children1 = db.relationship("Ad_request", back_populates="parent1", cascade="all, delete-orphan")
    parent1 = db.relationship("User", back_populates="children2")

    def to_dict(self):
        return {
            "campaign_id": self.campaign_id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            "end_date": self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            "budget": self.budget,
            "sponsor_id": self.sponsor_id,
            "visibility": self.visibility,
            "approved": self.approved,
            "status": self.status,
        }


class Ad_request(db.Model):
    adrequest_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey(Campaign.campaign_id))
    influencer_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
    requirements = db.Column(db.String, nullable=False)
    payment_amount = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)  # Pending/Accepted/Rejected/Completed
    sent_by = db.Column(db.String, nullable=False)  # sponsor/influencer
    date_of_joining = db.Column(db.Date, nullable=True)
    negotiation_amount = db.Column(db.String, nullable=True)
    negotiation_message = db.Column(db.String, nullable=True)

    parent1 = db.relationship("Campaign", back_populates="children1")
    parent2 = db.relationship("User", back_populates="children1")

    def to_dict(self):
        return {
            "adrequest_id": self.adrequest_id,
            "campaign_id": self.campaign_id,
            "influencer_id": self.influencer_id,
            "requirements": self.requirements,
            "payment_amount": self.payment_amount,
            "status": self.status,
            "sent_by": self.sent_by,
            "date_of_joining": self.date_of_joining.strftime('%Y-%m-%d') if self.date_of_joining else None,
            "negotiation_amount": self.negotiation_amount,
            "negotiation_message": self.negotiation_message,
        }


class Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    amount = db.Column(db.String, nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey(Campaign.campaign_id))
    influencer_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
    date_of_payment = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "payment_id": self.payment_id,
            "amount": self.amount,
            "campaign_id": self.campaign_id,
            "influencer_id": self.influencer_id,
            "date_of_payment": self.date_of_payment.strftime('%Y-%m-%d'),
        }
