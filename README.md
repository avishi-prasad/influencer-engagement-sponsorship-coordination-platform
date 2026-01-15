# Influencer Engagement and Sponsorship Coordination Platform

## **App Name** : AdConnect

## Description
- A platform to connect Sponsors and Influencers so that sponsors can get their product/service advertised and influencers can get monetary benefit.

## Frameworks used
- Flask  
- Vue JS  
- Jinja2 templates 
- Bootstrap  
- SQLite for database  
- Redis for caching 
- Redis and Celery for batch jobs

## Roles
The platform has three roles:
1. Admin
  - root access
  - An admin can monitor all the users/campaigns, see all the statistics
  - Ability to flag inappropriate campaigns/users


2. Sponsors 
  - a company/individual who wants to advertise their product/service
  - Sponsors will create campaigns, search for influencers and send ad requests for a particular campaign.
  - Sponsors can create multiple campaigns and track each individual campaign.
  - They can accept ad requests by influencers for public campaigns.
  - Each Sponsor has:
    - Company Name / Individual Name
    - Industry
    - Budget


3. Influencers
  - an individual who has significant social media following
  - An influencer will receive ad requests, accept or reject ad requests, negotiate terms and resend modified ad requests back to sponsors.
  - They can search for ongoing campaigns (which are public), according to category, budget etc. and accept the request.
  - An influencer can update their profile page, which is publicly visible.
  - Each Influencer profile has:
    - Name
    - Category
    - Niche
    - Reach (calculated by number of followers / activity etc.)
   
## Terminologies
  - **Ad request** : A contract between campaign and influencer, stating the requirements of the particular advertisement
  - **Campaign** : A container for ads requests for a particular goal. It can have multiple Ad requests, a campaign description, budget.

## Funtionalities
1. Authentication & Role-Based Access (RBAC)
- Login and registration for **Admin, Sponsor, and Influencer**
- Single admin identified by role
- Unified user model to differentiate user types

2. Admin Dashboard
- Admin auto-created when database is initialized
- Approval of new sponsor registrations
- Dashboard displays:
  - Active users
  - Campaigns 
  - Ad requests and their status
  - Flagged sponsors and influencers

3. Campaign Management (Sponsor)
- Create campaigns with niche categorization
- Update campaign details (start date, end date, budget, etc.)
- Delete campaigns

4. Ad Request Management (Sponsor)
- Create ad requests based on campaign goals
- Edit ad request details (influencer, requirements, payment amount, status)
- Delete ad requests
  
5. Search & Discovery
- Sponsors search influencers by niche, reach, and followers
- Influencers search public campaigns by relevance and niche

6. Influencer Actions
- View all ad requests across campaigns
- Accept or reject ad requests
- Negotiate payment amount

7. Backend Jobs & Automation
- Daily reminders to influencers via email
- Monthly activity reports for sponsors (HTML/PDF via email)
- Async CSV export of campaign data triggered by sponsors

8. Performance & Caching
- Caching for frequently accessed data

9. Additional Enhancements
- Frontend and backend form validation
- Add-to-desktop support


