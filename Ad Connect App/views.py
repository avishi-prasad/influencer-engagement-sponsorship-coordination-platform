from flask import current_app as app,render_template,request,jsonify,redirect
from models import db,User,Campaign,Ad_request,Admin,Payment
from datetime import datetime,date,timedelta
from sqlalchemy import and_, or_
from main import get_cached_data, set_cache,mail 
import json
from hashlib import sha256
from flask_mail import Message
import csv
import os


#-USER-LOGIN------------------------------------------------------------------------------------------

@app.route("/")
def userlogin():
    return render_template("user_login.html")
#-ADMIN-LOGIN------------------------------------------------------------------------------------------

@app.route("/adminlogin")
def adminlogin():
    ad=Admin.query.all()
    if(len(ad)==1):
        pass
    else:
        admin=Admin(admin_id="app_admin_00",admin_pass="@1029")
        db.session.add(admin)
        db.session.commit()
    return render_template("admin_login.html")

#-ADMIN-DASHBOARD------------------------------------------------------------------------------------------

@app.route("/admin_dashboard")
def admin_dashboard():
    users=User.query.all()
    u=len(users)
    camps=Campaign.query.filter_by(status="active").all()
    unapproved_campaigns=[]
    unapproved_sponsors=[]
    unapproved_influencers=[]
    for i in camps:
        sp_id=i.sponsor_id
        sp=User.query.filter_by(user_role="sponsor",user_id=sp_id).first().user_name
        i.sponsor_id=sp
        if i.approved==None:
            unapproved_campaigns.append(i)
    c=len(camps)
    req=Ad_request.query.all()
    reqs=[]
    for i in req:
        if(i.status=="pending" or i.status=="accepted"):
            reqs.append(i)
    r=len(reqs)
    unapproved_sponsors=User.query.filter_by(user_role="sponsor",approved=None).all()
    unapproved_influencers=User.query.filter_by(user_role="influencer",approved=None).all()
    
    return render_template("admin_dashboard.html",total_users=u,total_campaigns=c,unapproved_influencers=unapproved_influencers,total_ad_requests=r,unapproved_sponsors=unapproved_sponsors,unapproved_campaigns=unapproved_campaigns)

#-FLAG/APPROVE-------------------------------------------------------------------------------------------
@app.route("/approve/sponsor/<sponsor_id>")
def approve_sp(sponsor_id):
    user=User.query.filter_by(user_id=sponsor_id).first()
    user.approved="approved"
    db.session.add(user)
    db.session.commit()
    return redirect("/admin_dashboard")

@app.route("/approve/influencer/<inf_id>")
def approve_inf(inf_id):
    user=User.query.filter_by(user_id=inf_id).first()
    user.approved="approved"
    db.session.add(user)
    db.session.commit()
    return redirect("/admin_dashboard")

@app.route("/approve/campaign/<campaign_id>")
def approve_camp(campaign_id):
    camp=Campaign.query.filter_by(campaign_id=campaign_id,status="active").first()
    camp.approved="approved"
    db.session.add(camp)
    db.session.commit()
    return redirect("/admin_dashboard")

@app.route("/flag/sponsor/<sponsor_id>")
def flag_sp(sponsor_id):
    user=User.query.filter_by(user_id=sponsor_id).first()
    user.approved="flagged"
    db.session.add(user)
    db.session.commit()
    return redirect("/admin_dashboard")

@app.route("/flag/influencer/<inf_id>")
def flag_inf(inf_id):
    user=User.query.filter_by(user_id=inf_id).first()
    user.approved="flagged"
    db.session.add(user)
    db.session.commit()
    return redirect("/admin_dashboard")

@app.route("/flag/campaign/<campaign_id>")
def flag_camp(campaign_id):
    camp=Campaign.query.filter_by(campaign_id=campaign_id,status="active").first()
    camp.approved="flagged"
    db.session.add(camp)
    db.session.commit()
    return redirect("/admin_dashboard")

#-USER-LOGIN------------------------------------------------------------------------------------------

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    role = data.get('role')
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(user_role=role, user_name=username).first()
    if user:
        if user.user_pass == password:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Invalid password'})
    else:
        return jsonify({'success': False, 'message': 'No user found'})

#-USER-REGISTER------------------------------------------------------------------------------------------

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    role = data.get('role')
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(user_role=role, user_name=username).first()
    if user:
        return jsonify({'success': False, 'message': 'User already exists. Please try another username'})
    else:
        new_user = User(user_role=role, user_name=username, user_pass=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True})

@app.route("/userlogin/<user_role>/<user_name>")
def user_dashboard(user_role, user_name):
    if user_role == "influencer":
        return render_template("inf_dashboard.html", username=user_name)
    if user_role == "sponsor":
        return render_template("sp_dashboard.html", username=user_name)

#-INFLUENCER-PROFILE------------------------------------------------------------------------------------------

@app.route("/influencer/<username>/profile")
def inf_profile(username):
    user=User.query.filter_by(user_name=username).first()
    if(user.approved=="flagged"):
        return render_template("inf_dashboard.html",username=username,flagged=True)
    rating=user.rating
    description=user.description
    followers=user.followers
    earnings_this_month=float(0)
    category=user.category
    approved=user.approved
    if not followers:
        followers=0
    if((len(str(followers)))>3):
        followers=str(followers/1000)+"K"
    inf_id=user.user_id
    ad_requests=Ad_request.query.filter_by(influencer_id=inf_id).all()
    pending=[]
    pending_sent_by_inf=[]
    accepted=[]
    rejected=[]
    rejected_by_sp=[]
    completed=[]
    pending_campaigns=[]
    rejected_campaigns=[]
    nego_req=[]
    active_requests=[]
    inactive_campaigns=[]
    for i in ad_requests:
        if(i.status=="pending"):
            if i.negotiation_amount:
                nego_req.append(i)
            else:
                if(i.sent_by=="sponsor"):
                    pending.append(i)
                if(i.sent_by=="influencer"):
                    pending_sent_by_inf.append(i)
        if(i.status=="accepted"):
            accepted.append(i)
        if(i.status=="rejected"):
            if(i.sent_by=="sponsor"):
                    rejected.append(i)
                    if(i.negotiation_message=="**rejected_negotiation**"):
                        rejected_by_sp.append(i)
            if(i.sent_by=="influencer"):
                    rejected_by_sp.append(i)
        if(i.status=="completed"):
            completed.append(i)
    for i in rejected_by_sp:
        c_id=i.campaign_id
        c=Campaign.query.filter_by(campaign_id=c_id).first()
        if(c and c.status=="active"):
            sp_id=c.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            i.sponsor_name=sp.user_name
            i.camp_name=c.name
            i.camp_approved=c.approved
            i.sp_approved=sp.approved
            i.end_date=c.end_date
            if(i.negotiation_message=="**rejected_negotiation**"):
                i.nego_rej=True
        if(c and c.status=="inactive"):
            rejected_by_sp.remove(i)
    for i in pending_sent_by_inf:
        c_id=i.campaign_id
        c=Campaign.query.filter_by(campaign_id=c_id).first()
        if(c and c.status=="active"):
            sp_id=c.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            i.sponsor_name=sp.user_name
            i.camp_name=c.name
            i.camp_approved=c.approved
            i.sp_approved=sp.approved
            i.end_date=c.end_date
        if(c and c.status=="inactive"):
            pending_sent_by_inf.remove(i)
    for i in pending:
        pc={}
        c_id=i.campaign_id
        c=Campaign.query.filter_by(campaign_id=c_id).first()
        if(c and c.status=="active"):
            c_name=c.name
            c_app=c.approved
            sp_id=c.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            sp_name=sp.user_name
            sp_app=sp.approved
            i.campaign_name=c_name
            i.sponsor_name=sp_name
            i.camp_approved=c_app
            i.sp_approved=sp_app
            i.end_date=c.end_date
            i.start_date=c.start_date
        if(c and c.status=="inactive"):
            pending.remove(i)
    for i in rejected:
        rc={}
        c_id=i.campaign_id
        c=Campaign.query.filter_by(campaign_id=c_id).first()
        if(c and c.status=="active"):
            c_name=c.name
            c_app=c.approved
            sp_id=c.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            sp_name=sp.user_name
            sp_app=sp.approved
            i.campaign_name=c_name
            i.sponsor_name=sp_name
            i.camp_approved=c_app
            i.sp_approved=sp_app
            i.end_date=c.end_date
            i.start_date=c.start_date
        if(c and c.status=="inactive"):
            rejected.remove(i)
    for i in accepted:
        ac={}
        c_id=i.campaign_id
        c=Campaign.query.filter_by(campaign_id=c_id).first()
        if(c and c.status=="active"):
            c_name=c.name
            c_app=c.approved
            sp_id=c.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            sp_name=sp.user_name
            sp_app=sp.approved
            i.campaign_name=c_name
            i.sponsor_name=sp_name
            i.camp_approved=c_app
            i.sp_approved=sp_app
            i.end_date=c.end_date
            i.start_date=c.start_date
        if(c and c.status=="inactive"):
            accepted.remove(i)
    for i in nego_req:
        c_id=i.campaign_id
        c=Campaign.query.filter_by(campaign_id=c_id).first()
        if(c and c.status=="active"):
            c_name=c.name
            c_app=c.approved
            sp_id=c.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            sp_name=sp.user_name
            sp_app=sp.approved
            i.campaign_name=c_name
            i.sponsor_name=sp_name
            i.camp_approved=c_app
            i.sp_approved=sp_app
        if(c and c.status=="inactive"):
            nego_req.remove(i)
    payments=Payment.query.filter_by(influencer_id=user.user_id).all()
    for i in payments:
        d1=str(i.date_of_payment).split("-")
        d2=str(date.today()).split("-")
        if(d1[1]==d2[1]):
            earnings_this_month+=float(i.amount)
    return render_template("inf_dashboard.html",email=user.email,pending_sent_by_inf=pending_sent_by_inf,rejected_by_sp=rejected_by_sp,nego_requests=nego_req,approved=approved,profile=True,user_id=inf_id,username=username,category=category,earnings=earnings_this_month,rating=rating,description=description,followers=followers,active_requests=accepted,inactive_campaigns=inactive_campaigns,pending_requests=pending,rejected_requests=rejected)

#-sponsor-PROFILE------------------------------------------------------------------------------------------

@app.route("/sponsor/<username>/profile")
def sp_profile(username):
    user=User.query.filter_by(user_name=username).first()
    if(user.approved=="flagged"):
        return render_template("sp_dashboard.html",username=username,flagged=True)
    sp_id=user.user_id
    category=user.category
    approved=user.approved
    camp=Campaign.query.filter_by(sponsor_id=sp_id).all()
    camps=[]
    ending_campaigns=[]
    pending_req=[]
    pending_requests_by_sp=[]
    count=0
    for i in camp:
        ad_req=Ad_request.query.filter_by(campaign_id=i.campaign_id,sent_by="influencer",status="pending").all()
        if ad_req:
            for i in ad_req:
                pending_req.append(i)
    for i in pending_req:
        inf_id=i.influencer_id
        inf=User.query.filter_by(user_id=inf_id).first()
        inf_name=inf.user_name
        i.inf_name=inf_name
        camp_id=i.campaign_id
        c=Campaign.query.filter_by(campaign_id=camp_id).first()
        if(c and c.status=="active"):
            camp_name=c.name
            i.camp_name=camp_name
            i.camp_approved=c.approved
            sp_id=c.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            i.inf_approved=inf.approved
        if(c and c.status=="inactive"):
            pending_req.remove(i)
    for i in camp:
        ad_req=Ad_request.query.filter_by(campaign_id=i.campaign_id,sent_by="sponsor",status="pending").all()
        if ad_req:
            for i in ad_req:
                pending_requests_by_sp.append(i)
    for i in pending_requests_by_sp:
        inf_id=i.influencer_id
        inf=User.query.filter_by(user_id=inf_id).first()
        inf_name=inf.user_name
        i.inf_name=inf_name
        camp_id=i.campaign_id
        c=Campaign.query.filter_by(campaign_id=camp_id).first()
        if(c and c.status=="active"):
            camp_name=c.name
            i.camp_name=camp_name
            i.camp_approved=c.approved
            sp_id=c.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            i.inf_approved=inf.approved
        if(c and c.status=="inactive"):
            pending_requests_by_sp.remove(i)
    
    if camp:
        for i in camp:
            if(i.status=='active'):
                camps.append(i)
                count+=1
                if(i.end_date<=date.today()):
                    ending_campaigns.append(i)
    for i in ending_campaigns:
        if(i.end_date==date.today()):
            i.ending_today=True
        if(i.end_date<date.today()):
            i.ending_passed=True
    return render_template("sp_dashboard.html",email=user.email,pending_requests_by_sp=pending_requests_by_sp,sp_id=sp_id,no_of_active_camps=count,approved=approved,username=username,pending_requests=pending_req,profile=True,category=category,active_campaigns=camps,ending_campaigns=ending_campaigns)

#-SP-NEGO-MESSAGES-----------------------------------------------------------------------------------------

@app.route("/sponsor/<username>/messages")
def sp_msges(username):
    user=User.query.filter_by(user_name=username).first()
    camps=Campaign.query.filter_by(sponsor_id=user.user_id).all()
    negotiated_req=[]
    if camps:
        for i in camps:
            c_id=i.campaign_id
            
            req=Ad_request.query.filter_by(campaign_id=c_id).all()
            for j in req:
                if j.negotiation_amount:
                    print(j)
                    cp_id=j.campaign_id
                    c=Campaign.query.filter_by(campaign_id=cp_id).first()
                    j.camp_name=c.name
                    j.camp_approved=c.approved
                    inf_id=j.influencer_id
                    inf=User.query.filter_by(user_id=inf_id).first()
                    j.inf_name=inf.user_name
                    j.sp_approved=inf.approved
                    negotiated_req.append(j)
    else:
        pass

    if negotiated_req:
        negotiated_req.reverse()
    
    return render_template("sp_dashboard.html",username=username,messages=True,entries=negotiated_req)

#-ADD-CAMPAIGN------------------------------------------------------------------------------------------

@app.route("/sponsor/<username>/add_campaign")
def add_campaign(username):
    user=User.query.filter_by(user_name=username).first()
    sp_id=user.user_id
    camps=Campaign.query.filter_by(sponsor_id=sp_id,status="active").all()
    for i in camps:
        if(i.end_date==date.today()):
            i.ending_today=True
        if(i.end_date<date.today()):
            i.ending_passed=True
    ended_camps=Campaign.query.filter_by(sponsor_id=sp_id,status="inactive").all()
    return render_template("sp_dashboard.html",username=username,campaign=True,active_campaigns=camps, ended_campaigns=ended_camps)
    

@app.route("/sponsor/<username>/add_new_campaign", methods=['GET', 'POST'])
def new_campaign(username):
    if request.method == 'GET':
        return render_template("sp_dashboard.html", campaign=True, username=username, show=True)
    if request.method == 'POST':
        try:
            user = User.query.filter_by(user_name=username).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404

            sp_id = user.user_id
            
            data = request.get_json()
            print(f"Received data: {data}")
            
            name = data['name']
            description = data['description']
            start_date = date.today()
            budget = data['budget']
            end_date=data['end_date']
            
            if not name or not description or not start_date or not budget or not end_date:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            # Convert start_date to a proper date object
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            existing_camp=Campaign.query.filter_by(name=name,sponsor_id=sp_id).first()
            if(existing_camp):
                print("Campaign name already exists.")
                return None
            # Store data in the database
            new_campaign = Campaign(
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date_obj,
                budget=budget,
                sponsor_id=sp_id,
                status='active'
            )
            db.session.add(new_campaign)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Campaign added successfully'})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

#-EDIT-CAMPAIGN------------------------------------------------------------------------------------------

@app.route("/sponsor/<username>/edit_campaign/<camp_id>", methods=['GET', 'POST'])
def edit_campaign(username,camp_id):
    if request.method == 'POST':
        try:
            user = User.query.filter_by(user_name=username).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            camp = Campaign.query.filter_by(campaign_id=camp_id).first()
            if not camp:
                return jsonify({'success': False, 'message': 'Campaign not found'}), 404
            sp_id = user.user_id
            
            data = request.get_json()
            print(f"Received data: {data}")
            
            name = data['name']
            description = data['description']
            budget = data['budget']
            end_date=data['end_date']
            
            if not name or not description or not budget or not end_date:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            # Convert start_date to a proper date object
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            old_budget=camp.budget
            camp.name=name
            camp.description=description
            camp.budget=budget
            camp.end_date=end_date_obj

            ad_req=Ad_request.query.filter_by(campaign_id=camp_id,payment_amount=old_budget).all()
            for i in ad_req:
                i.payment_amount=budget
                db.session.add(i)
            
            db.session.add(camp)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Campaign added successfully'})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

#-DELETE-CAMPAIGN------------------------------------------------------------------------------------------

@app.route("/sponsor/<username>/delete_camp/<camp_id>",methods=["GET","POST"])
def delete_campaign(username,camp_id):
    camp=Campaign.query.filter_by(campaign_id=camp_id).first()
    db.session.delete(camp)
    db.session.commit()
    return redirect(f"/sponsor/{username}/add_campaign")

#-INF-SEARCH------------------------------------------------------------------------------------------

# Helper function to generate a cache key based on parameters
def generate_cache_key(prefix, **kwargs):
    key_string = f"{prefix}:{','.join([f'{k}={v}' for k, v in kwargs.items()])}"
    return sha256(key_string.encode()).hexdigest()
    
@app.route("/influencer/<username>/search", methods=['GET', 'POST'])
def search_inf(username):
    if request.method == "GET":
        # Cache key for all active campaigns
        cache_key = f"active_campaigns"
        cached_camps = get_cached_data(cache_key)
        
        if cached_camps:
            # Load campaigns as dictionaries from cache
            camps = json.loads(cached_camps)
        else:
            # Query campaigns and convert them to dictionaries
            camps = [c.to_dict() for c in Campaign.query.filter_by(status="active").all()]
            set_cache(cache_key, json.dumps(camps), timeout=10)  # Cache for 10 minutes
        
        # Add sponsor details to the cached or queried campaign data
        for i in camps:
            sp = User.query.filter_by(user_role="sponsor", user_id=i['sponsor_id']).first()
            i['sponsor_name'] = sp.user_name
            i['camp_approved'] = i['approved']
            i['sp_approved'] = sp.approved
            i['category'] = sp.category

        camps.reverse()
        return render_template("inf_dashboard.html", username=username, search=True, campaigns=camps)

    if request.method == "POST":
        data = request.get_json()
        query = data.get("query", "").lower()
        category = data.get("category", "").lower()
        min_budget = data.get("min_budget", 0)
        max_budget = data.get("max_budget", float('inf'))

        # Generate a unique cache key for the search parameters
        cache_key = generate_cache_key("search_results", query=query, category=category, min_budget=min_budget, max_budget=max_budget)
        cached_results = get_cached_data(cache_key)
        
        if cached_results:
            results = json.loads(cached_results)
        else:
            filters = [Campaign.status == "active"]
            if query:
                filters.append(or_(Campaign.name.ilike(f"%{query}%"),
                                   User.user_name.ilike(f"%{query}%")))
            if category:
                filters.append(User.category.ilike(f"%{category}%"))
            if min_budget:
                filters.append(Campaign.budget >= min_budget)
            if max_budget:
                filters.append(Campaign.budget <= max_budget)

            camps = Campaign.query.join(User, Campaign.sponsor_id == User.user_id).filter(and_(*filters)).all()
            results = [c.to_dict() for c in camps]
            
            # Cache the results
            set_cache(cache_key, json.dumps(results), timeout=10)  # Cache for 10 minutes

        if not results:
            return jsonify({'success': False})

        return jsonify({'success': True, 'campaigns': [r['campaign_id'] for r in results]})


@app.route("/influencer/<username>/search_results", methods=['GET', 'POST'])
def search_results(username):
    if request.method == 'GET':
        camp_id = request.args.get('campaign_ids') 
        print(camp_id)
        camps = []
        
        if not camp_id or camp_id == "[]":
            return render_template("inf_dashboard.html", search=True, username=username, campaigns=camps, msg=True)
        
        # Generate a cache key for specific campaign IDs
        cache_key = generate_cache_key("campaign_results", campaign_ids=camp_id)
        cached_camps = get_cached_data(cache_key)

        if cached_camps:
            # Load campaigns as dictionaries from cache
            camps = json.loads(cached_camps)
        else:
            camp_id = camp_id.split(',')
            for i in camp_id:
                c = Campaign.query.filter_by(campaign_id=i, status="active").first()
                if c:
                    camps.append(c.to_dict())
            set_cache(cache_key, json.dumps(camps), timeout=10)  # Cache for 10 minutes

        # Add sponsor details to the campaign data
        for i in camps:
            sp = User.query.filter_by(user_role="sponsor", user_id=i['sponsor_id']).first()
            i['sponsor_name'] = sp.user_name
            i['camp_approved'] = i['approved']
            i['sp_approved'] = sp.approved
            i['category'] = sp.category

        if len(camps) != 0:
            camps.reverse()
        
        return render_template("inf_dashboard.html", search=True, username=username, campaigns=camps, result=True)

#-SP-SEARCH------------------------------------------------------------------------------------------

@app.route("/sponsor/<username>/search", methods=['GET', 'POST'])
def sp_search(username):
    if request.method == "GET":
        # Cache key for all influencers
        cache_key = "all_influencers"
        cached_infs = get_cached_data(cache_key)
        
        if cached_infs:
            # Load influencers as dictionaries from cache
            infs = json.loads(cached_infs)
        else:
            # Query all influencers and convert to dicts
            infs = [i.to_dict() for i in User.query.filter_by(user_role="influencer").all()]
            set_cache(cache_key, json.dumps(infs), timeout=10)  # Cache for 10 minutes
        
        infs.reverse()
        return render_template("sp_dashboard.html", username=username, search=True, influencers=infs)
    
    if request.method == "POST":
        data = request.get_json()
        query = data.get("searchQuery", "").lower()
        category = data.get("category", "").lower()
        min_followers = data.get("minFollowers", 0)
        min_rating = data.get("minRating", 0)

        filters = [User.user_role == "influencer"]

        if query:
            filters.append(User.user_name.ilike(f"%{query}%"))
        
        if category:
            filters.append(User.category.ilike(f"%{category}%"))

        if min_followers:
            filters.append(User.followers >= min_followers)
        
        if min_rating:
            filters.append(User.rating >= min_rating)

        infs = User.query.filter(and_(*filters)).all()

        if not infs:
            return jsonify({'success': False})
        
        results = [i.user_id for i in infs]
        
        if results:
            return jsonify({'success': True, 'influencers': results})
        else:
            return jsonify({'success': False, 'influencers': []})


@app.route("/sponsor/<username>/search_results", methods=['GET', 'POST'])
def sp_search_results(username):
    if request.method == 'GET':
        inf_id = request.args.get('influencer_ids')
        
        infs = []
        if not inf_id or inf_id == "[]":
            return render_template("sp_dashboard.html", search=True, username=username, influencers=infs, msg=True)
        
        # Generate cache key for specific influencer IDs
        cache_key = generate_cache_key("influencer_results", influencer_ids=inf_id)
        cached_infs = get_cached_data(cache_key)

        if cached_infs:
            # Load influencers as dictionaries from cache
            infs = json.loads(cached_infs)
        else:
            inf_id = inf_id.split(',')
            for i in inf_id:
                c = User.query.filter_by(user_id=i).first()
                if c:
                    infs.append(c.to_dict())
            set_cache(cache_key, json.dumps(infs), timeout=10)  # Cache for 10 minutes

        if len(infs) != 0:
            infs.reverse()
        
        return render_template("sp_dashboard.html", search=True, username=username, influencers=infs, result=True)

#-INF-EDIT-DESCRIPTION-------------------------------------------------------------------------------------

@app.route("/inf/edit_desc/<username>",methods=['POST'])
def edit_desc(username):
    if request.method == 'POST':
        try:
            user = User.query.filter_by(user_name=username).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404

            inf_id = user.user_id
            
            data = request.get_json()
            print(f"Received data: {data}")
        
            desc = data["description"]
            if not desc:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            # Convert start_date to a proper date object
            #start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Store data in the database
            user.description=desc
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Desc edited successfully'})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
        
#-INF-EDIT-FOLLOWERS-----------------------------------------------------------------------------------------
        
@app.route("/inf/edit_followers/<username>",methods=['POST'])
def edit_foll(username):
    if request.method == 'POST':
        try:
            user = User.query.filter_by(user_name=username).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404

            inf_id = user.user_id
            
            data = request.get_json()
            print(f"Received data: {data}")
        
            foll = data["followers"]
            if not foll:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            # Convert start_date to a proper date object
            #start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Store data in the database
            user.followers=foll
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Followers edited successfully'})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
        
#-INF-EDIT-CATEGORY-----------------------------------------------------------------------------------------

@app.route("/inf/edit_category/<username>",methods=['POST'])
def edit_catgeory(username):
    if request.method == 'POST':
        try:
            user = User.query.filter_by(user_name=username).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404

            inf_id = user.user_id
            
            data = request.get_json()
            print(f"Received data: {data}")
        
            cat = data["category"]
            if not cat:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            # Convert start_date to a proper date object
            #start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Store data in the database
            user.category=cat
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Followers edited successfully'})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

#-SP-EDIT-CATEGORY-----------------------------------------------------------------------------------------

@app.route("/sponsor/edit_category/<username>",methods=['POST'])
def edit_sp_catgeory(username):
    if request.method == 'POST':
        try:
            user = User.query.filter_by(user_name=username).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404

            inf_id = user.user_id
            
            data = request.get_json()
            print(f"Received data: {data}")
        
            cat = data["category"]
            if not cat:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            # Convert start_date to a proper date object
            #start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Store data in the database
            user.category=cat
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Followers edited successfully'})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
#-INF-EMAIL-----------------------------------------------------------------------------------------------
@app.route("/inf/edit_email/<username>",methods=['POST'])
def edit_email(username):
    if request.method == 'POST':
        try:
            user = User.query.filter_by(user_name=username).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404

            inf_id = user.user_id
            
            data = request.get_json()
            print(f"Received data: {data}")
        
            email = data["email"]
            if not email:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            # Convert start_date to a proper date object
            #start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Store data in the database
            user.email=email
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Email edited successfully'})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route("/sponsor/edit_email/<username>",methods=['POST'])
def edit_sp_email(username):
    if request.method == 'POST':
        try:
            user = User.query.filter_by(user_name=username).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404

            inf_id = user.user_id
            
            data = request.get_json()
            print(f"Received data: {data}")
        
            email = data["email"]
            if not email:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            # Convert start_date to a proper date object
            #start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Store data in the database
            user.email=email
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Followers edited successfully'})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
#-SP-SEARCH-FOR-INF-----------------------------------------------------------------------------------------

@app.route("/sponsor/<username>/details/inf/<inf_id>",methods=["GET","POST"])
def inf_details_for_sp(username,inf_id):
    if request.method == 'GET':
        inf=User.query.filter_by(user_id=inf_id).first()
        followers=inf.followers
        if not followers:
            followers=0
        if((len(str(followers)))>3):
            followers=str(followers/1000)+"K"
        campaigns=[]
        
        sp_id=User.query.filter_by(user_role="sponsor",user_name=username).first().user_id
        camps=Campaign.query.filter_by(sponsor_id=sp_id,status="active").all()
        for i in camps:
            ad=Ad_request.query.filter_by(influencer_id=inf.user_id,campaign_id=i.campaign_id).all()
            if(ad):
                pass
            else:
                camp={}
                camp["id"]=i.campaign_id
                camp["name"]=i.name
                campaigns.append(camp)
        current_camp=[]
        r=Ad_request.query.filter_by(status="accepted",influencer_id=inf_id).all()
        for i in r:
            ac={}
            c_id=i.campaign_id
            c=Campaign.query.filter_by(status="active",campaign_id=c_id).first()
            sp_id=c.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            
            ac["adrequest_id"]=i.adrequest_id
            ac["campaign_id"]=c_id
            ac["campaign_name"]=c.name
            ac["sponsor_name"]=sp.user_name
            ac["pay_amount"]=i.payment_amount
            ac["requirements"]=i.requirements
            ac["approved"]=c.approved
            ac["sp_approved"]=sp.approved
            current_camp.append(ac)
        
        completed_camp=[]
        r=Ad_request.query.filter_by(status="completed",influencer_id=inf_id).all()
        for i in r:
            ac={}
            c_id=i.campaign_id
            c=Campaign.query.filter_by(campaign_id=c_id).first()
            sp_id=c.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            ac["adrequest_id"]=i.adrequest_id
            ac["campaign_id"]=c_id
            ac["campaign_name"]=c.name
            ac["sponsor_name"]=sp.user_name
            ac["pay_amount"]=i.payment_amount
            ac["requirements"]=i.requirements
            ac["approved"]=c.approved
            ac["sp_approved"]=sp.approved
            completed_camp.append(ac)
        
        

        return render_template("sp_details.html",username=username,campaigns=campaigns,INF=True,inf_id=inf.user_id,inf_name=inf.user_name,influencer=inf,current_camp=current_camp,completed_camp=completed_camp,followers=followers)
    if request.method == 'POST':
        try:
            user = User.query.filter_by(user_name=username).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404

            sp_id = user.user_id
            
            data = request.get_json()
            print(f"Received data: {data}")
            
            campaign_id = data['campaign_id']
            influencer_id = data['inf_id']
            inf=User.query.filter_by(user_id=influencer_id).first()
    
            if not campaign_id or not influencer_id :
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            camp=Campaign.query.filter_by(campaign_id=campaign_id).first()
            c=camp.budget
            amt=(int(c[0])+int(c[1]))/2
            print(amt)
            new_req = Ad_request(
                campaign_id=campaign_id,
                influencer_id=influencer_id,
                requirements=camp.description,
                payment_amount=c,
                status='pending',
                sent_by="sponsor"
            )
            db.session.add(new_req)
            db.session.commit()
            if inf.email:
                msg = Message(
                subject='New ad request',
                recipients=[f'{inf.email}'],  # List of recipients
                body=f'New ad request from {username} for campaign: {camp.name}',
                )
                mail.send(msg)
            return jsonify({'success': True, 'message': 'Request sent successfully'})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
        
#-SP-SEARCH-FOR-CAMP-----------------------------------------------------------------------------------------

@app.route("/sponsor/<username>/details/camp/<camp_id>")
def camp_details_for_sp(username,camp_id):
    camp=Campaign.query.filter_by(status="active",campaign_id=camp_id).first()
    sp_id=camp.sponsor_id
    sp=User.query.filter_by(user_id=sp_id).first()
    camp.sponsor_id=sp.user_name
    camp.sp_approved=sp.approved
    req1=Ad_request.query.filter_by(campaign_id=camp_id,status="accepted").all()
    #req2=Ad_request.query.filter_by(campaign_id=camp_id,status="completed").all()
    return render_template("sp_details.html",username=username,CAMP=True,campaigns=[],camp=camp,infs=len(req1))

#-INF-SEARCH-FOR-CAMP-----------------------------------------------------------------------------------------

@app.route("/influencer/<username>/details/camp/<camp_id>" , methods=["GET","POST"])
def camp_details_for_inf(username,camp_id):
    if request.method == 'POST':
        try:
            user = User.query.filter_by(user_name=username).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404

            data = request.get_json()
            print(f"Received data: {data}")
            
            campaign_id = data['campaign_id']
            influencer_id = data['inf_id']
            sp_id = Campaign.query.filter_by(campaign_id=campaign_id).first().sponsor_id
            sp= User.query.filter_by(user_id=sp_id).first()
    
            if not campaign_id or not influencer_id :
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            camp=Campaign.query.filter_by(campaign_id=campaign_id).first()
            c=camp.budget
            amt=(int(c[0])+int(c[1]))/2
            
            new_req = Ad_request(
                campaign_id=campaign_id,
                influencer_id=influencer_id,
                requirements=camp.description,
                payment_amount=c,
                status='pending',
                sent_by='influencer'
            )
            db.session.add(new_req)
            db.session.commit()
            if sp.email:
                msg = Message(
                subject='New ad request',
                recipients=[f'{sp.email}'],  # List of recipients
                body=f'New ad request from {username} for campaign: {camp.name}',
                )
                mail.send(msg)
            
            return jsonify({'success': True, 'message': 'Request sent successfully'})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
    inf=User.query.filter_by(user_name=username).first()
    camp=Campaign.query.filter_by(status="active",campaign_id=camp_id).first()
    sp_id=camp.sponsor_id
    sp=User.query.filter_by(user_id=sp_id).first()
    camp.sponsor_id=sp.user_name
    camp_name=camp.name
    camp.sp_approved=sp.approved
    req1=Ad_request.query.filter_by(campaign_id=camp_id,status="accepted").all()
    
    if(req1):
        req1=len(req1)
    else:
        req1=0

    r=Ad_request.query.filter_by(influencer_id=inf.user_id,campaign_id=camp_id).first()
    
    if( r ):
        return render_template("inf_details.html",username=username,camp_name=camp_name,campaign=camp,infs=req1,influencer=inf,requested=True)
    return render_template("inf_details.html",username=username,camp_name=camp_name,campaign=camp,infs=req1,influencer=inf,requested=False)

#-INF-ACCEPT/REJECT-REQUEST------------------------------------------------------------------------------------------

@app.route("/influencer/<username>/accept_request/<adrequest_id>")
def accept_request_by_sp(username,adrequest_id,):
    req=Ad_request.query.filter_by(adrequest_id=adrequest_id,status="pending").first()
    req.status="accepted"
    req.date_of_joining=date.today()
    db.session.add(req)
    db.session.commit()
    return redirect(f"/influencer/{username}/profile")

@app.route("/influencer/<username>/reject_request/<adrequest_id>")
def reject_request_by_sp(username,adrequest_id,):
    req=Ad_request.query.filter_by(adrequest_id=adrequest_id).first()
    req.status="rejected"
    db.session.add(req)
    db.session.commit()
    return redirect(f"/influencer/{username}/profile")

#-SP-ACCEPT/REJECT-REQUEST------------------------------------------------------------------------------------------

@app.route("/sponsor/<username>/accept_request/<adrequest_id>")
def accept_request_by_inf(username,adrequest_id,):
    req=Ad_request.query.filter_by(adrequest_id=adrequest_id,status="pending").first()
    req.status="accepted"
    req.date_of_joining=date.today()
    db.session.add(req)
    db.session.commit()
    return redirect(f"/sponsor/{username}/profile")

@app.route("/sponsor/<username>/reject_request/<adrequest_id>")
def reject_request_by_inf(username,adrequest_id,):
    req=Ad_request.query.filter_by(adrequest_id=adrequest_id,status="pending").first()
    req.status="rejected"
    db.session.add(req)
    db.session.commit()
    return redirect(f"/sponsor/{username}/profile")

#-INF-ACCEPT/REJECT-NEGO-REQUEST------------------------------------------------------------------------------------------

@app.route("/influencer/<username>/accept_negotiation_request/<adrequest_id>")
def accept_nego_request(username,adrequest_id):
    ad_req=Ad_request.query.filter_by(adrequest_id=adrequest_id).first()
    new_pay=ad_req.negotiation_amount
    ad_req.payment_amount=new_pay
    ad_req.status="accepted"
    ad_req.date_of_joining=date.today()
    ad_req.negotiation_message=None
    ad_req.negotiation_amount=None
    db.session.add(ad_req)
    db.session.commit()
    return redirect(f"/sponsor/{username}/messages")

@app.route("/influencer/<username>/reject_negotiation_request/<adrequest_id>")
def reject_nego_request(username,adrequest_id):
    ad_req=Ad_request.query.filter_by(adrequest_id=adrequest_id).first()
    ad_req.status="rejected"
    ad_req.negotiation_message="**rejected_negotiation**"
    ad_req.negotiation_amount=None
    db.session.add(ad_req)
    db.session.commit()
    return redirect(f"/sponsor/{username}/messages")

#-INF-REACCEPT-REQUEST------------------------------------------------------------------------------------------
@app.route("/influencer/<username>/reaccept_adrequest/<adrequest_id>")
def reccept_adrequest(username,adrequest_id):
    ad_req=Ad_request.query.filter_by(adrequest_id=adrequest_id).first()
    ad_req.status="accepted"
    ad_req.date_of_joining=date.today()
    ad_req.negotiation_message=None
    db.session.add(ad_req)
    db.session.commit()
    return redirect(f"/influencer/{username}/profile")

#-DELETE-ADREQUEST------------------------------------------------------------------------------------------
@app.route("/influencer/<username>/delete_adrequest/<adrequest_id>")
def del_request_by_inf(username,adrequest_id):
    ad_req=Ad_request.query.filter_by(adrequest_id=adrequest_id,sent_by="influencer").first()
    db.session.delete(ad_req)
    db.session.commit()
    return redirect(f"/influencer/{username}/profile")

@app.route("/sponsor/<username>/delete_adrequest/<adrequest_id>")
def del_request_by_sp(username,adrequest_id):
    ad_req=Ad_request.query.filter_by(adrequest_id=adrequest_id,sent_by="sponsor").first()
    db.session.delete(ad_req)
    db.session.commit()
    return redirect(f"/sponsor/{username}/profile")

#-SP-RATE-INF------------------------------------------------------------------------------------------

@app.route("/sponsor/<username>/rate/inf/<inf_id>",methods=["GET","POST"])
def rate_inf(username,inf_id):
    if request.method == 'POST':
        try:
            user = User.query.filter_by(user_name=username).first()
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404

            sp_id = user.user_id
            
            data = request.get_json()
            print(f"Received data: {data}")
        
            influencer_id = data['inf_id']
            rating = data['rating']
            if not rating or not influencer_id :
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            inf=User.query.filter_by(user_id=influencer_id).first()
            old_rating=inf.rating
            if(old_rating==None):
                old_rating=0
                new_rating=int(rating)
            else:
                new_rating=int((old_rating+int(rating))/2)
            inf.rating=new_rating
            db.session.add(inf)
            db.session.commit()
            
            return jsonify({'success': True}),200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

#-INF-NEGOTIATE-REQUEST------------------------------------------------------------------------------------------

@app.route("/influencer/<username>/negotiate/<adrequest_id>",methods=["GET","POST"])
def negotiate(username,adrequest_id):
    if request.method=="GET":
        req=Ad_request.query.filter_by(adrequest_id=adrequest_id).first()
        camp_id=req.campaign_id
        camp=Campaign.query.filter_by(campaign_id=camp_id).first()
        sp_id=camp.sponsor_id
        sp=User.query.filter_by(user_id=sp_id).first()
        camp.sp_name=sp.user_name
        camp.sp_approved=sp.approved
        return render_template("negotiate.html",username=username,adrequest_id=adrequest_id,campaign=camp)
    if request.method=="POST":
        amt=request.form['amt']
        msg=request.form['msg']
        ad_request=Ad_request.query.filter_by(adrequest_id=adrequest_id).first()
        camp_id=ad_request.campaign_id
        camp=Campaign.query.filter_by(campaign_id=camp_id).first()
        camp_name=camp.name
        sp_id=camp.sponsor_id
        sp=User.query.filter_by(user_id=sp_id).first()
        ad_request.negotiation_amount=amt
        if msg:
            ad_request.negotiation_message=msg
        db.session.add(ad_request)
        db.session.commit()
        if sp.email:
            mail_msg = Message(
                subject='New negotiation request',
                recipients=[f'{sp.email}'],  # List of recipients
                body=f'New negotiation request from {username} for campaign: {camp_name}',
                )
            mail.send(mail_msg)

        return render_template("inf_dashboard.html",amt=amt,msg=msg,negotiation=True,username=username,camp_name=camp_name)

#-END-CAMPAIGN------------------------------------------------------------------------------------------
@app.route("/sponsor/<username>/end_campaign_page/<campaign_id>", methods=["GET","POST"])
def end_campaign_page(username,campaign_id):
    if request.method=="GET":
        camp=Campaign.query.filter_by(campaign_id=campaign_id).first()
        ad_reqs=Ad_request.query.filter_by(campaign_id=campaign_id,status="accepted").all()
        count=len(ad_reqs)
        total_amount=float(0)
        for i in ad_reqs:
            inf_id=i.influencer_id
            inf=User.query.filter_by(user_id=inf_id).first()
            i.inf_name=inf.user_name
            i.inf_approved=inf.approved
            if("-" in i.payment_amount):
                range=(i.payment_amount).split("-")
                a1=range[0]
                a2=range[1]
                a1=int(a1)
                a2=int(a2)
                amount=int((a1+a2)/2)
                i.payment_amount=amount
        for i in ad_reqs:
            total_amount+=float(i.payment_amount)
        if(camp.status=="active"):
            camp_ended=False
        if(camp.status=="inactive"):
            camp_ended=True
        return render_template("pay_n_end.html",camp_ended=camp_ended,total_amount=total_amount,username=username,x=camp,requests=ad_reqs,count=count)
    
@app.route("/sponsor/<username>/end_campaign/<campaign_id>", methods=["GET","POST"])
def end_campaign(username,campaign_id):
    if request.method=="GET":
        camp=Campaign.query.filter_by(campaign_id=campaign_id).first()
        ad_reqs=Ad_request.query.filter_by(campaign_id=campaign_id,status="accepted").all()
        for i in ad_reqs:
            if("-" in i.payment_amount):
                range=(i.payment_amount).split("-")
                a1=range[0]
                a2=range[1]
                a1=int(a1)
                a2=int(a2)
                amount=int((a1+a2)/2)
                i.payment_amount=amount
            new_payment=Payment(campaign_id=campaign_id,influencer_id=i.influencer_id,amount=i.payment_amount,date_of_payment=date.today())
            i.status="completed"
            db.session.add(i)
            db.session.add(new_payment)

        camp.status="inactive"
        camp.end_date=date.today()
        db.session.add(camp)
        
        db.session.commit()
    return redirect(f"/sponsor/{username}/end_campaign_page/{campaign_id}")

#-TRACK-CAMPAIGN--------------------------------------------------------------------------------------
@app.route("/sponsor/<username>/view_camp/<campaign_id>", methods=["GET","POST"])
def track_camp(username,campaign_id):
    if request.method=="GET":
        camp=Campaign.query.filter_by(campaign_id=campaign_id).first()
        ad_reqs=Ad_request.query.filter_by(campaign_id=campaign_id,status="accepted").all()
        count=len(ad_reqs)
        total_amount=float(0)
        for i in ad_reqs:
            inf_id=i.influencer_id
            inf=User.query.filter_by(user_id=inf_id).first()
            i.inf_name=inf.user_name
            i.inf_approved=inf.approved
            if("-" in i.payment_amount):
                range_=(i.payment_amount).split("-")
                a1=range_[0]
                a2=range_[1]
                a1=int(a1)
                a2=int(a2)
                amount=int((a1+a2)/2)
                i.payment_amount=amount
        for i in ad_reqs:
            total_amount+=float(i.payment_amount)
        if(camp.status=="active"):
            camp_ended=False
        if(camp.status=="inactive"):
            camp_ended=True
        
        rejected=Ad_request.query.filter_by(campaign_id=campaign_id,status="rejected",sent_by="sponsor").all()
        
        for i in rejected:
            inf_id=i.influencer_id
            inf=User.query.filter_by(user_id=inf_id).first()
            i.inf_name=inf.user_name
            i.inf_approved=inf.approved

        days_passed=""
        days_left=""
        end_date=camp.end_date
        time_left=end_date-date.today()
        if(str(time_left)=="0:00:00"):
            last_day=True
        else:
            last_day=False
            d=str(time_left).split(",")
            days_left=d[0]
            if("-" in str(days_left)):
                days_passed=days_left[1:]
                days_left=""

        reach_data = []  
        start_date = camp.start_date
        today = date.today()
        date_to_reach = {} 

        for req in ad_reqs:
            influencer = User.query.filter_by(user_id=req.influencer_id).first()
            if req.date_of_joining and influencer.followers:
                join_date = req.date_of_joining
                followers = influencer.followers
                if join_date not in date_to_reach:
                    date_to_reach[join_date] = followers
                else:
                    date_to_reach[join_date] += followers
        
        cumulative_reach = 0
        n = (today - start_date).days + 1
        for i in range(n):
            single_date = start_date + timedelta(days=i)
            cumulative_reach += date_to_reach.get(single_date, 0)
            reach_data.append({"date": single_date.strftime("%Y-%m-%d"), "total_reach": cumulative_reach})
            

        return render_template("track_camp.html",reach_data=reach_data,rejected=rejected,last_day=last_day,days_passed=days_passed,days_left=days_left,camp_ended=camp_ended,total_amount=total_amount,username=username,x=camp,requests=ad_reqs,count=count)
    
#-ADMIN-VIEW------------------------------------------------------------------------------------------------------

@app.route("/admin/view_campaigns")
def admin_view_camp():
    camps=Campaign.query.filter_by(status="active").all()
    if(camps):
        for i in camps:
            sp_id=i.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            i.sponsor_name=sp.user_name
    else:
        camps=[]
    return render_template("admin_view.html",CAMP=True,camps=camps,inf_to_rating=[],inf_to_followers=[],inf_to_activity=[],sp_to_activity=[])

@app.route("/admin/view_influencers")
def admin_view_inf():
    cache_key = "admin_view_influencers"
    cached_data = get_cached_data(cache_key)

    if cached_data:
        cached_data = json.loads(cached_data)
        return render_template(
            "admin_view.html",
            INF=True,
            infs=cached_data["infs"],
            inf_to_rating=cached_data["inf_to_rating"],
            inf_to_followers=cached_data["inf_to_followers"],
            inf_to_activity=cached_data["inf_to_activity"],
            sp_to_activity=[]
        )

    # If no cached data, compute the values
    infs = User.query.filter_by(user_role="influencer").all()

    inf_to_rating = {}
    for i in infs:
        if i.user_name and i.rating:
            inf_to_rating[i.user_name] = i.rating

    if inf_to_rating:
        inf_to_rating = dict(sorted(inf_to_rating.items(), key=lambda x: x[1], reverse=True))

    inf_to_followers = {}
    for i in infs:
        if i.user_name and i.followers:
            inf_to_followers[i.user_name] = i.followers

    inf_to_activity = {}
    for i in infs:
        ads = Ad_request.query.filter_by(influencer_id=i.user_id).all()
        if ads:
            inf_to_activity[i.user_name] = len(ads)

    # Limit to top 10 if necessary
    if len(infs) > 10:
        inf_to_activity = dict(sorted(inf_to_activity.items(), key=lambda x: x[1], reverse=False)[:10])
        inf_to_followers = dict(sorted(inf_to_followers.items(), key=lambda x: x[1], reverse=False)[:10])
        inf_to_rating = dict(sorted(inf_to_rating.items(), key=lambda x: x[1], reverse=False))
    else:
        inf_to_rating = dict(sorted(inf_to_rating.items(), key=lambda x: x[1], reverse=False))
        inf_to_followers = dict(sorted(inf_to_followers.items(), key=lambda x: x[1], reverse=False))
        inf_to_activity = dict(sorted(inf_to_activity.items(), key=lambda x: x[1], reverse=False))

    # Prepare data for caching
    data_to_cache = {
        "infs": [inf.to_dict() for inf in infs],  # Use a `to_dict()` method for serialization
        "inf_to_rating": inf_to_rating,
        "inf_to_followers": inf_to_followers,
        "inf_to_activity": inf_to_activity,
    }

    set_cache(cache_key, json.dumps(data_to_cache), timeout=10)
    return render_template(
        "admin_view.html",
        INF=True,
        infs=infs,
        inf_to_rating=inf_to_rating,
        inf_to_followers=inf_to_followers,
        inf_to_activity=inf_to_activity,
        sp_to_activity=[]
    )

@app.route("/admin/view_sponsors")
def admin_view_sp():
    # Check if sponsor activity data is cached in Redis
    cached_data = get_cached_data("sp_to_activity")
    
    if cached_data:
        sp_to_activity = json.loads(cached_data)
    else:
        sps = User.query.filter_by(user_role="sponsor").all()
        sp_to_activity = {}

        if sps:
            for sponsor in sps:
                sp_id = sponsor.user_id
                campaigns = Campaign.query.filter_by(sponsor_id=sp_id).all()
                num_campaigns = len(campaigns)
                num_ads = 0

                if campaigns:
                    for campaign in campaigns:
                        ads = Ad_request.query.filter_by(campaign_id=campaign.campaign_id).all()
                        num_ads += len(ads)

                sp_to_activity[sponsor.user_name] = num_campaigns + num_ads

        # Cache the computed data in Redis
        set_cache("sp_to_activity", json.dumps(sp_to_activity), timeout=10)  # Expire in 10 minutes (10 seconds)

    # Handle case with more than 10 sponsors
    if len(sp_to_activity) > 10:
        sp_to_activity = dict(sorted(sp_to_activity.items(), key=lambda x: x[1], reverse=False)[:10])
    
    return render_template(
        "admin_view.html",
        SP=True,
        sps=User.query.filter_by(user_role="sponsor").all(),  # Pass all sponsors for display
        sp_to_activity=sp_to_activity,
        inf_to_rating=[],
        inf_to_followers=[],
        inf_to_activity=[]
    )


@app.route("/admin/inf_detail/<inf_id>")
def admin_inf_detail(inf_id):
    inf=User.query.filter_by(user_id=inf_id).first()
    if not inf.followers:
        inf.followers=0
    if((len(str(inf.followers)))>3):
        inf.followers=str(inf.followers/1000)+"K"
    acc_req=Ad_request.query.filter_by(influencer_id=inf_id,status="accepted").all()
    done_req=Ad_request.query.filter_by(influencer_id=inf_id,status="completed").all()
    joined_camps=[]
    if acc_req or done_req:
        joined_camps=acc_req+done_req
        for i in joined_camps:
            c=Campaign.query.filter_by(campaign_id=i.campaign_id).first()
            sp_id=c.sponsor_id
            sp=User.query.filter_by(user_id=sp_id).first()
            i.sponsor_name=sp.user_name
            i.campaign_name=c.name
            i.camp_approved=c.approved
            i.sp_approved=sp.approved
    
    return render_template("admin_detail_view.html",INF=True,inf=inf,joined_camps=joined_camps,reach_data=[])

@app.route("/admin/sp_detail/<sp_id>")
def admin_sp_detail(sp_id):
    sp=User.query.filter_by(user_id=sp_id).first()
    active_camps=Campaign.query.filter_by(sponsor_id=sp_id,status="active").all()
    done_camps=Campaign.query.filter_by(sponsor_id=sp_id,status="inactive").all()
    for i in active_camps:
        ads=Ad_request.query.filter_by(campaign_id=i.campaign_id).all()
        i.infs=len(ads)
    for i in done_camps:
        ads=Ad_request.query.filter_by(campaign_id=i.campaign_id).all()
        i.infs=len(ads)
    total_camps=active_camps+done_camps
    return render_template("admin_detail_view.html",SP=True,reach_data=[],sp=sp,total_camps=total_camps,done_camps=done_camps,active_camps=active_camps)

@app.route("/admin/camp_detail/<campaign_id>")
def admin_camp_detail(campaign_id):
    if request.method=="GET":
        camp=Campaign.query.filter_by(campaign_id=campaign_id).first()
        sp_id=camp.sponsor_id
        sp=User.query.filter_by(user_id=sp_id).first()
        camp.sponsor_name=sp.user_name
        camp.sp_approved=sp.approved
        ad_reqs=Ad_request.query.filter_by(campaign_id=campaign_id,status="accepted").all()
        count=len(ad_reqs)
        total_amount=float(0)
        for i in ad_reqs:
            inf_id=i.influencer_id
            inf=User.query.filter_by(user_id=inf_id).first()
            i.inf_name=inf.user_name
            i.inf_approved=inf.approved
            if("-" in i.payment_amount):
                range_=(i.payment_amount).split("-")
                a1=range_[0]
                a2=range_[1]
                a1=int(a1)
                a2=int(a2)
                amount=int((a1+a2)/2)
                i.payment_amount=amount
        for i in ad_reqs:
            total_amount+=float(i.payment_amount)
        if(camp.status=="active"):
            camp_ended=False
        if(camp.status=="inactive"):
            camp_ended=True
    

        days_passed=""
        days_left=""
        end_date=camp.end_date
        time_left=end_date-date.today()
        if(str(time_left)=="0:00:00"):
            last_day=True
        else:
            last_day=False
            d=str(time_left).split(",")
            days_left=d[0]
            if("-" in str(days_left)):
                days_passed=days_left[1:]
                days_left=""

        reach_data = []  
        start_date = camp.start_date
        today = date.today()
        date_to_reach = {} 

        for req in ad_reqs:
            influencer = User.query.filter_by(user_id=req.influencer_id).first()
            if req.date_of_joining and influencer.followers:
                join_date = req.date_of_joining
                followers = influencer.followers
                if join_date not in date_to_reach:
                    date_to_reach[join_date] = followers
                else:
                    date_to_reach[join_date] += followers

        cumulative_reach = 0
        n = (today - start_date).days + 1
        for i in range(n):
            single_date = start_date + timedelta(days=i)
            cumulative_reach += date_to_reach.get(single_date, 0)
            reach_data.append({"date": single_date.strftime("%Y-%m-%d"), "total_reach": cumulative_reach})
        
            

    return render_template("admin_detail_view.html",CAMP=True,reach_data=reach_data,last_day=last_day,days_passed=days_passed,days_left=days_left,camp_ended=camp_ended,total_amount=total_amount,x=camp,requests=ad_reqs,count=count)

@app.route('/sponsor/<username>/get_report/<campaign_id>', methods=['GET'])
def send_campaign_report(username, campaign_id):
    try:
        campaign=Campaign.query.filter_by(campaign_id=campaign_id).first()
        sp_id=campaign.sponsor_id
        sp=User.query.filter_by(user_id=sp_id).first()
        campaign.budget_used = 0.0
        ads = Ad_request.query.filter_by(campaign_id=campaign.campaign_id).all()
        campaign.ad_count = len(ads)
        campaign.reach = 0
        date_to_reach = {}

        for ad in ads:
            if ad.status == "accepted":
                if("-" in ad.payment_amount):
                    range_=(ad.payment_amount).split("-")
                    a1=range_[0]
                    a2=range_[1]
                    a1=int(a1)
                    a2=int(a2)
                    amount=int((a1+a2)/2)
                    ad.payment_amount=amount
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

        campaign_details = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "start_date": campaign.start_date,
            "end_date": campaign.end_date,
            "total_ads":campaign.ad_count,
            "budget_used": campaign.budget_used,
        }

        
        csv_file_path = f"./campaign_report.csv"
        with open(csv_file_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(campaign_details.keys())  
            writer.writerow(campaign_details.values())  

        if(sp.email):
            msg = Message(
                subject=f"Campaign Report for Campaign ID {campaign_id}",
                recipients=[f"{sp.email}"], 
                body=f"Hello {username},\n\nPlease find the attached report for Campaign ID {campaign_id}."
            )
            with app.open_resource(csv_file_path) as attachment:
                msg.attach(
                    filename=f"campaign_{campaign_id}_report.csv",
                    content_type="text/csv",
                    data=attachment.read(),
                )

            mail.send(msg)
        else:
            return render_template("sp_dashboard.html",username=username,report=True,no_email=True)
        os.remove(csv_file_path)

        return render_template("sp_dashboard.html",username=username,report=True,sent=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500