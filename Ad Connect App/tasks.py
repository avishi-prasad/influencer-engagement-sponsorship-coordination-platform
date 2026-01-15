from flask import current_app as app
from models import User, Campaign, Ad_request
from datetime import datetime, date
from flask_mail import Message
from flask import render_template
from main import mail
from celery_config import celery_app

@celery_app.task
def schedule_monthly_reports():
    import logging
    logging.info("Executing schedule_monthly_reports task.")
    def generate_monthly_report(sponsor_id):
        sponsor = User.query.filter_by(user_role="sponsor").first() 

        if not sponsor:
            return f"Sponsor with ID {sponsor_id} not found."
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.user_id, status="active").all()

        for campaign in campaigns:
            campaign.budget_used = 0.0
            ads = Ad_request.query.filter_by(campaign_id=campaign.campaign_id).all()
            campaign.ad_count = len(ads)
            campaign.reach = 0
            date_to_reach = {}

            for ad in ads:
                if ad.status == "accepted":
                    campaign.budget_used += float(ad.payment_amount)

                    influencer = User.query.filter_by(user_id=ad.influencer_id).first()
                    if ad.date_of_joining and influencer.followers:
                        join_date = ad.date_of_joining
                        followers = influencer.followers
                        if join_date not in date_to_reach:
                            date_to_reach[join_date] = followers
                        else:
                            date_to_reach[join_date] += followers

            today = date.today()
            campaign.reach = date_to_reach.get(today, 0)

        
        total_ads = sum(campaign.ad_count for campaign in campaigns)
        budget_used = sum(campaign.budget_used for campaign in campaigns)

        
        current_month = datetime.now().strftime("%B %Y")

        
        html_content = render_template(
            'monthly_report.html',
            sponsor=sponsor,
            current_month=current_month,
            campaigns=campaigns,
            total_ads=total_ads,
            budget_used=budget_used
        )

        if sponsor.email:
            msg = Message(
                subject=f"Monthly Report - {current_month}",
                recipients=[sponsor.email],  
                html= html_content
            )
            mail.send(msg)


        return f"Monthly report sent to {sponsor.email}"

    with app.app_context():
        sponsors = User.query.filter_by(user_role="sponsor").all()
        for sponsor in sponsors:
            generate_monthly_report.apply_async(args=[sponsor.user_id])
