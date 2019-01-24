from flask import (
        Flask,
        render_template,
        redirect,
        url_for,
        request,
        jsonify,
        make_response,
        flash
    )
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from config import CLIENT_ID

import random
import string
import json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import requests
import httplib2

from db_setup import Base, User, Alliance, Airline

################################################################################
# init
################################################################################
app = Flask(__name__)
app.config.from_pyfile('config.py')

# for dev
engine = create_engine('sqlite:///airlines_alliances_catalog.db?check_same_thread=False')

# for prod
# engine = create_engine('sqlite:///airlines_alliances_catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


################################################################################
# logins and authentication section
################################################################################

# helper for checking authentication and registration
def getUser(uid):
    try:
        return session.query(User).filter_by(id=uid).one()
    except:
        return None


def isRegistered(email):
    # pass
    # check if the signed in visitor is a registered customer in User
    try:
        uid = session.query(User.id).filter_by(email=email).one()
        return True
    except:
        return False

def registerUser(login_session):
    # pass
    # reigster a new user in the User table based on login session
    name = login_session["username"]
    email = login_session["email"]
    picture = login_session["picture"]

    newUser = User(email=email, name=name, picture=picture)
    session.add(newUser)
    session.commit()

    uid = session.query(User.id).filter_by(email=email).one()
    return uid[0]

@app.route("/login")
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state

    # print(login_session)

    return render_template("login.html", STATE=state)
    # return "future home of google login"

## reference to Udacity github ud330 step 5
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    try:
        login_session['username'] = data['name']
    except:
        login_session["username"] = "Google User"

    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check if user is registered from previous logins

    print(isRegistered(login_session["email"]))
    if not isRegistered(login_session["email"]):
        user_id = registerUser(login_session)
    else:
        user_id = session.query(User).filter_by(email=login_session["email"]).first()
        user_id = user_id.id

    # save the user's id from User table to use later
    login_session["user_id"] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now sucessfully logged in ")
    # print "done!"

    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'

        flash("You are now successfully logged out")
        return redirect(url_for('index'), code=302)
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

    # return "future home of google disconnect"

################################################################################
# views
################################################################################
@app.route("/")
def index():

    alliances = session.query(Alliance).all()
    # last 4 entries
    latest_airlines = session.query(Airline).order_by(desc(Airline.id)).limit(4)

    # print(alliances)
    # print(latest_airlines)

    return render_template('catalog.html', alliances=alliances, latest_airlines=latest_airlines)


@app.route("/alliance/<int:id>")
@app.route("/alliance/<int:id>/airlines")
def showAlliance(id):
    one_alliance = session.query(Alliance).filter_by(id=id).first()
    _airlines = session.query(Airline).filter_by(aid=one_alliance.id).all()
    airline_count = len(_airlines)

    op = getUser(one_alliance.uid)
    # print(op)

    return render_template("alliances.html", alliance=one_alliance, airlines=_airlines, airline_count=airline_count, op=op)


@app.route('/alliance/<int:alliance_id>/airline/<int:airline_id>')
def showAirline(alliance_id, airline_id):
    airline = session.query(Airline).filter_by(**{"id":airline_id, "aid":alliance_id}).first()
    # testing op
    op = getUser(airline.uid)

    return render_template('airlines.html', airline=airline, op=op)


################################################################################
# CRUD - alliance related
################################################################################

@app.route('/alliance/new/', methods=['GET', 'POST'])
def newAlliance():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newAlliance = Alliance(name=request.form['name'], uid=login_session["user_id"])
        session.add(newAlliance)
        session.commit()
        flash('New Alliance %s Successfully Created' % newAlliance.name)
        return redirect(url_for('index'))
    else:
        return render_template('new_alliance.html')


@app.route('/alliance/<int:alliance_id>/edit/', methods=['GET', 'POST'])
def editAlliance(alliance_id):
    if 'username' not in login_session:
        return redirect('/login')

    editedAlliance = session.query(Alliance).filter_by(id=alliance_id).one()
    op = getUser(editedAlliance.uid)

    if op.id != login_session["user_id"]:
        flash("You are not the original creator of this entry. Please sign in as the creator or modify a different etry.")
        return redirect('/login')

    if request.method == 'POST':
        if request.form['name']:
            editedAlliance.name = request.form['name']
            flash('Alliance successfully edited %s' % editedAlliance.name)
            return redirect(url_for('index'))
    else:
        return render_template('edit_alliance.html', alliance=editedAlliance)


@app.route('/alliance/<int:alliance_id>/delete/', methods=['GET', 'POST'])
def deleteAlliance(alliance_id):
    if 'username' not in login_session:
        return redirect('/login')

    allianceToDelete = session.query(Alliance).filter_by(id=alliance_id).one()
    op = getUser(allianceToDelete.uid)

    if op.id != login_session["user_id"]:
        flash("You are not the original creator of this entry. Please sign in as the creator or modify a different etry.")
        return redirect('/login')

    if request.method == 'POST':
        session.delete(allianceToDelete)
        session.commit()
        flash('%s Successfully deleted' % allianceToDelete.name)
        return redirect(url_for('index'))
    else:
        return render_template('delete_alliance.html', alliance=allianceToDelete)


################################################################################
# CRUD - airline related
################################################################################

@app.route('/alliance/<int:alliance_id>/airline/new/', methods=['GET', 'POST'])
def newAirline(alliance_id):
    if 'username' not in login_session:
        return redirect('/login')

    try:
        alliance = session.query(Alliance).filter_by(id=alliance_id).one()
    except:
        return "The alliance that you are trying to add an airline to does not exist. Please try again."

    op = getUser(alliance.uid)

    if op.id != login_session["user_id"]:
        flash("You are not the original creator of this entry. Please sign in as the creator or modify a different etry.")
        return redirect('/login')

    if request.method == 'POST':
        newAirline = Airline(name=request.form['name'],
                             description=request.form["description"],
                             miles=request.form["miles"],
                             aid=alliance_id,
                             uid=login_session["user_id"]
                            )
        session.add(newAirline)
        session.commit()
        flash('New airline %s successfully created' % newAirline.name)
        return redirect(url_for('showAlliance', id=alliance_id))
    else:
        return render_template('new_airline.html', alliance=alliance)


@app.route('/alliance/<int:alliance_id>/airline/<int:airline_id>/edit/', methods=['GET', 'POST'])
def editAirline(alliance_id, airline_id):
    if 'username' not in login_session:
        return redirect('/login')

    editedAirline = session.query(Airline).filter_by(**{"id":airline_id, "aid":alliance_id}).one()
    op = getUser(editedAirline.uid)

    if op.id != login_session["user_id"]:
        flash("You are not the original creator of this entry. Please sign in as the creator or modify a different etry.")
        return redirect('/login')

    if request.method == 'POST':
        if request.form['name']:
            editedAirline.name = request.form['name']
            editedAirline.description = request.form["description"]
            editedAirline.miles = request.form["miles"]
            flash('Airline successfully edited %s' % editedAirline.name)
            return redirect(url_for('showAirline', alliance_id=alliance_id, airline_id=editedAirline.id))
        # return "future home of airline edit"
    else:
        return render_template('edit_airline.html', alliance_id=alliance_id, airline=editedAirline)


@app.route('/alliance/<int:alliance_id>/airline/<int:airline_id>/delete/', methods=['GET', 'POST'])
def deleteAirline(alliance_id, airline_id):
    if 'username' not in login_session:
        return redirect('/login')

    airlineToDelete = session.query(Airline).filter_by(**{"id":airline_id, "aid":alliance_id}).one()
    op = getUser(airlineToDelete.uid)

    if op.id != login_session["user_id"]:
        flash("You are not the original creator of this entry. Please sign in as the creator or modify a different etry.")
        return redirect('/login')

    if request.method == "POST":
        session.delete(airlineToDelete)
        session.commit()
        flash('%s Successfully deleted' % airlineToDelete.name)
        return redirect(url_for('showAlliance', id=alliance_id))
        # return "future home of airline delete"
    else:
        return render_template("delete_airline.html", alliance_id=alliance_id, airline=airlineToDelete)

################################################################################
# API - JSON endpoints
################################################################################
@app.route("/api/alliances.json")
def showAlliancesJson():
    alliances = session.query(Alliance).all()
    output = []

    for alliance in alliances:
        airlines = session.query(Airline).filter_by(aid=alliance.id)
        _output = {}
        _output["alliance_id"] = alliance.id
        _output["alliance_name"] = alliance.name
        _output["alliance_airlines"] = [i.serialize for i in airlines]

        output.append(_output)

    return jsonify(output)


################################################################################
# run
################################################################################
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
