# 🧾 Bidding Platform — Backend (Django REST Framework + SQLite)

Project Overview

This project is the backend of an Online Bidding Platform where:
Admins can create, manage, and close auctions
Buyers can place bids on auctions
The system automatically closes auctions and determines the winner


## Tech Stack
- **Backend Framework:** Django REST Framework (DRF)  
- **Database:** SQLite  
- **Authentication:** JWT (JSON Web Token)  
- **ORM:** Django ORM  
- **Background Task:** Python thread (auto-close auctions)  

## Features
- User Roles: Admin & Buyer  
- Bid Rules: Must be higher than current highest + min_increment  
- Automatic auction closure  
- Winner determination (highest valid bid >= reserve price)

# create project dir and activate venv
mkdir bidding_platform
cd bidding_platform
python -m venv venv
source venv/bin/activate        # on Windows use `venv\Scripts\activate`

# install packages
pip install django djangorestframework djangorestframework-simplejwt

# create django project and app
django-admin startproject bidding_platform .
python manage.py startapp auctions


## Project Setup Instructions

1. Clone repo / create folder:
```bash
git clone <repo_url>
cd bidding_platform
```
2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate # Windows
# or
source venv/bin/activate # Linux/Mac
```
3. Install dependencies:
```bash
pip install django djangorestframework djangorestframework-simplejwt
```
4. Create Django project & apps:
```bash
django-admin startproject bidding_platform
cd bidding_platform
python manage.py startapp authentication
python manage.py startapp auctions
```
5. Apply migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```
6. Run server:
```bash
python manage.py runserver
```
Server URL → http://localhost:8000

 http://localhost:8000/auth/register/   like

## URL Structure Overview

| Area | URL | Method | Role |
|------|-----|--------|------|
| Register | `/auth/register/` | POST | Public |
| Login | `/auth/login/` | POST | Public |
| Create Auction | `/auctions/` | POST | Admin |
| List Active Auctions | `/auctions/active/` | GET | Public |
| Auction Detail | `/auctions/<id>/` | GET | Public |
| Place Bid | `/auctions/<id>/bid/` | POST | Buyer |
| Get Winner | `/auctions/<id>/winner/` | GET | Public |
| All Auctions (Admin) | `/admin/auctions/` | GET | Admin |
| Force Close Auction | `/admin/auctions/<id>/force-close/` | POST | Admin |

## Authentication
### Register
POST `http://localhost:8000/auth/register/`
```json
{
  "username": "buyer1",
  "password": "pass1234",
  "role": "buyer",
  "email": "b1@example.com"
}
```
### Login
POST `http://localhost:8000/auth/login/`
```json
{
  "username": "buyer1",
  "password": "pass1234"
}
```
Response:
```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```
Use JWT in header:
```
Authorization: Bearer <access_token>
```

## Auction APIs
### Create Auction (Admin)
POST `http://localhost:8000/auctions/`
Header: Authorization: Bearer <admin_token>
```json
{
  "title": "MacBook Pro 2025",
  "description": "Apple M3 16GB RAM",
  "starting_price": 1000,
  "reserve_price": 1200,
  "start_time": "2025-10-17T10:00:00Z",
  "end_time": "2025-10-17T11:00:00Z",
  "min_increment": 50
}
```
### Get Active Auctions
GET `http://localhost:8000/auctions/active/`
### Place Bid (Buyer)
POST `http://localhost:8000/auctions/1/bid/`
Header: Authorization: Bearer <buyer_token>
```json
{
  "amount": 1050
}
```
### Get Auction Details
GET `http://localhost:8000/auctions/1/`
### Get Winner
GET `http://localhost:8000/auctions/1/winner/`
### Admin View — All Auctions
GET `http://localhost:8000/admin/auctions/`
Authorization: Bearer <admin_token>

## Folder Structure
```
bidding_platform/
├── authentication/
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── auctions/
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── bidding_platform/
│   ├── settings.py
│   ├── urls.py
└── manage.py
```

## Postman Testing Order
1. Register admin → `/auth/register/`  
2. Register buyer → `/auth/register/`  
3. Login admin → `/auth/login/`  
4. Login buyer → `/auth/login/`  
5. Create auction → `/auctions/`  
6. List active auctions → `/auctions/active/`  
7. Place bid → `/auctions/1/bid/`  
8. Get auction details → `/auctions/1/`  
9. View winner → `/auctions/1/winner/`

## Background Job
- Python thread checks expired auctions every 1 minute  
- Closes auction automatically and assigns winner

## Author
**Shivam Tripathi**  
Email: shivamtripathi93758@gmail.com


