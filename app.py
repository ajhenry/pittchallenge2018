import os
from flask import Flask, request, abort, url_for, redirect, session, render_template, flash, jsonify
from flask_restful import reqparse, abort, Api, Resource, fields, marshal, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
from flask_cors import CORS
from flask_heroku import Heroku
#from models import Res, Web, PhoneNumbers, Plocations, Locations, Keywords

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
heroku = Heroku(app)
db = SQLAlchemy(app)

api = Api(app)
CORS(app)

app.config.update(dict(SEND_FILE_MAX_AGE_DEFAULT=0))

parser = reqparse.RequestParser()
parser.add_argument('keywords',type=str)
parser.add_argument('city',type=str)
parser.add_argument('state',type=str)
parser.add_argument('national',type=bool)

# configuration
SECRET_KEY = "b''\xa7+\x17\xf2\x9b\xc5?\x91\x19\x19=\xfe\x8e\xf2?\x95.\x8c\x9c\x93A0\xca'"

app.config.from_object(__name__)
app.config.from_envvar('RESOURCE_SETTINGS', silent=True)



phones = {
    "number": fields.Integer,
    "sms_capable": fields.Boolean
}

location_fields = {
    "lon": fields.Integer,
    "lat": fields.Integer,
    "city": fields.String,
    "state": fields.String
}

physical_field = {
    "name": fields.String,
    "location": fields.Nested(location_fields)
}

resource = {
        "name": fields.String,
        "description": fields.String,
        "websites": fields.List(fields.String),
        "phone_numbers":fields.Nested(phones),
        "national": fields.Boolean,
        "physical_locations": fields.Nested(physical_field),
        "keywords": fields.List(fields.String)
}

resource_test = {
        "name": "Cool hospital",
        "description": "Awesome treatment",
        "websites": [
            "www.google.com",
            "www.bing.com"
        ],
        "phone_numbers": 
            {
                "number": "5",
                "sms_capable": True
            }
        ,
        "national": True,
        "physical_locations": 
            {
                "name": "downtown",
                "location": 
                    {
                        "lon": 5,
                        "lat": 5,
                        "city": "Pittsburgh",
                        "state": "PA"
                    }
                
            }
        ,
        "keywords": [
            "abuse",
            "opiods"
        ]
}

@app.route('/')
def default():
    """Only one page for application"""
    return render_template('index.html')

class AllResources(Resource):
    @marshal_with(resource)
    def get(self):
        args = parser.parse_args()
        print(args)
        q = None
        if args['keywords']:
            keywords = args['keywords'].split(',')
        else: 
            keywords = None
        
        if args['city']:
            city = args['city']
        else: 
            city = None
        
        if args['state']:
            state = args['state']
        else: 
            state = None

        if keywords:
            #limit querey to keywords
            for k in keywords:
                print('filtering by keyword')
                q1 = Res.query.filter(Res.keywords.any(Keywords.word==k))
                if q is None and q1.count()>0:
                    q = q1
                elif q1.count()>0:
                    q = q1.union(q)
            if q is None:
                return 204
        else:
            q = Res.query


        if city and state:
            print("filtering by city and state")
            q = q.filter(Res.physical_locations.any(Plocations.location.any(Locations.city==city)),Res.physical_locations.any(Plocations.location.any(Locations.state==state)))
        elif city:
            print("filtering by city")
            q = q.filter(Res.physical_locations.any(Plocations.location.any(Locations.city==city)))
        elif state:
            print("filtering by state")
            q = q.filter(Res.physical_locations.any(Plocations.location.any(Locations.state==state)))
            

        if q is None and city is None and state is None and keywords is None:
            q = Res.query
        elif q is None:
            return 200
        return q.all()
    
    def post(self):
        print("post Test log 1")
        json_data = request.get_json(force=True)
        print(json_data)
        print("post Test log 2")
        for result in json_data:
            res = Res(str(result['name']),str(result['description']),bool(result['national']))
            if result['websites']:
                for w in result['websites']:
                    web = Web(str(w))
                    res.websites.append(web)
            
            if result['phone_numbers']:
                for p in result['phone_numbers']:
                    pn = PhoneNumbers(str(p['number']),bool(p['sms_capable']))
                    res.phone_numbers.append(pn)
            
            if result['physical_locations']:
                for pp in result['physical_locations']:
                    p_loc = Plocations(str(pp['name']))
                    for l in pp['location']:
                        loc = Locations(int(l['lon']),int(l['lat']),str(l['city']),str(l['state']))    
                        p_loc.location.append(loc)
                    res.physical_locations.append(p_loc)
            for k in result['keywords']:
                key = Keywords(str(k))
                res.keywords.append(key)
            db.session.add(res)
        db.session.commit()
        return 200
            



api.add_resource(AllResources, '/resources')

class Res(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=False, nullable=False)
    description = db.Column(db.String(),unique=False, nullable=True)
    websites = db.relationship('Web', backref='res', lazy='joined')
    phone_numbers = db.relationship('PhoneNumbers', backref='res', lazy='joined')
    national = db.Column(db.Boolean)
    physical_locations = db.relationship('Plocations', backref='res', lazy='joined')
    keywords = db.relationship('Keywords', backref='res', lazy='joined')

    def __init__(self, name, description, national):
        self.name = name
        self.description = description
        self.national = national

class Web(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    res_id = db.Column(db.Integer, db.ForeignKey('res.id'), nullable=False)
    url = db.Column(db.String(), unique=False, nullable=False)

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return self.url

class PhoneNumbers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    res_id = db.Column(db.Integer, db.ForeignKey('res.id'), nullable=False)
    number = db.Column(db.String(), unique=False, nullable=False)
    sms_capable = db.Column(db.Boolean, unique=False, nullable=False)

    def __init__(self, number, sms_capable):
        self.number = number
        self.sms_capable = sms_capable

class Plocations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    res_id = db.Column(db.Integer, db.ForeignKey('res.id'), nullable=False)
    name = db.Column(db.String(), unique=False, nullable=False)
    location = db.relationship('Locations', backref='plocations', lazy='joined')

    def __init__(self, name):
        self.name = name

class Locations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plocations_id = db.Column(db.Integer, db.ForeignKey('plocations.id'), nullable=False)
    lon = db.Column(db.Integer, unique=False, nullable=False)
    lat = db.Column(db.Integer, unique=False,nullable=False)
    city = db.Column(db.String(), unique=False, nullable=False)
    state = db.Column(db.String(), unique=False, nullable=False)

    def __init__(self, lon, lat, city, state):
        self.lon = lon
        self.lat = lat
        self.city = city
        self.state = state

class Keywords(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    res_id = db.Column(db.Integer, db.ForeignKey('res.id'), nullable=False)
    word = db.Column(db.String(), unique=False,nullable=False)
    
    def __init__(self, word):
        self.word = word

    def __repr__(self):
        return self.word


if __name__ == "__main__":
    app.run(debug=True)