#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import datetime
import dateutil.parser
from flask_migrate import Migrate
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, literal
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

now = datetime.now()

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:Thinker1997@localhost:5432/fyyurdb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
engine = create_engine('postgresql://postgres:Thinker1997@localhost:5432/fyyurdb')
Session = sessionmaker(bind=engine)
session_ = Session()
session = db.session


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    genres = db.Column(db.String(120))
    shows = db.relationship("Show", cascade="all, delete")

    def __repr__(self):
          return f"<Venue> id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, genres: {self.genres}, facebook: {self.facebook_link}\n"

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))

    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    facebook_link = db.Column(db.String(120))
    def __repr__(self):
          return f"<Artist> id:{self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, genres: {self.genres}, facebook: {self.facebook_link}\n"

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.String, nullable=False)
    venue = db.relationship(Venue, backref='venue_show')
    artist = db.relationship(Artist, backref='artist_show')
    def __repr__(self):
      return f"<Show> venue ID: {self.venue_id}, artist ID: {self.artist_id}, start time: {self.start_time}\n"

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='full'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/')
def index():
  return render_template('pages/home.html')
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = session.query(Venue).all()
  cityStates = db.session.query(Venue.city, Venue.state).distinct().all()
  data = []
  for c in cityStates:
    if ", ".join(c).lower() not in data:
      data.append(", ".join(c).lower())
  return render_template('pages/venues.html', venues=venues, areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  searchterm= request.form.get('search_term')
  query = session.query(Venue).filter(func.lower(Venue.name).contains(func.lower(literal(searchterm)))).all()
  query_count = len(query)
  return render_template('pages/search_venues.html', results=query,query_count = query_count, search_term=searchterm)

# SHOW VENUE:-----------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = session.query(Venue).filter(Venue.id == venue_id).first_or_404()
  data = session.query(Artist, Show).join(Show, Show.venue_id == Artist.id).join(Venue, Show.venue_id == venue_id).all()
  l = str(venue.genres)
  # print(l.split)
  upcoming_shows=[]
  past_shows=[]

  for d in data:
    if (datetime.strptime(d.Show.start_time, "%Y-%m-%d %H:%M:%S") > now):
      upcoming_shows.append(d)
    elif(datetime.strptime(d.Show.start_time, "%Y-%m-%d %H:%M:%S") < now):
      past_shows.append(d)

  data1={
  "id": venue_id,
  "name": venue.name,
  "genres":[venue.genres],
  "address":venue.address,
  "city": venue.city,
  "state": venue.state,
  "phone": venue.phone,
  "website_link": venue.website_link,
  "facebook_link": venue.facebook_link,
  "seeking_talent": venue.seeking_talent,
  "seeking_description": venue.seeking_description,
  "image_link": venue.image_link,
  "past_shows": past_shows, 
  "upcoming_shows": upcoming_shows,
  "past_shows_count": len(past_shows),
  "upcoming_shows_count":len(upcoming_shows),
  }
  
  return render_template('pages/show_venue.html', venue = data1)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')

  seeking_description = request.form.get('seeking_description')

  if 'seeking_talent' not in request.form:
    seeking_talent = False
  else:
    seeking_talent =True
  website_link = request.form.get('website_link')
  image_link = request.form.get('image_link')

  try:
    venue = Venue(image_link=image_link,name=name, city=city, state=state, address=address,
                phone=phone, genres=genres, facebook_link=facebook_link, seeking_description= seeking_description,seeking_talent=seeking_talent, website_link=website_link )
    session_.add(venue)
    session_.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    session_.rollback()
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  finally:
    session_.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('The Venue has been successfully deleted!')
    return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('Delete was unsuccessful. Try again!')
  finally:
      db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = session.query(Artist).all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])

def search_artists():
  searchterm= request.form.get('search_term')
  query = session.query(Artist).filter(func.lower(Artist.name).contains(func.lower(literal(searchterm)))).all()
  query_count = len(query)
  return render_template('pages/search_artists.html', results=query,query_count = query_count, search_term=searchterm)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = session.query(Artist).filter(Artist.id == artist_id).first_or_404()
  data = session.query(Venue, Show).join(Show, Show.artist_id == Venue.id).join(Artist, Show.artist_id == artist_id).all()

  upcoming_shows=[]
  past_shows=[]
  
  for d in data:
    if (datetime.strptime(d.Show.start_time, "%Y-%m-%d %H:%M:%S") > now):
      upcoming_shows.append(d)
    elif(datetime.strptime(d.Show.start_time, "%Y-%m-%d %H:%M:%S") < now):
      past_shows.append(d)

  data1={
  "id": artist_id,
  "name": artist.name,
  "genres": artist.genres,
  "city": artist.city,
  "state": artist.state,
  "phone": artist.phone,
  "website": artist.website_link,
  "facebook_link": artist.facebook_link,
  "seeking_venue": artist.seeking_venue,
  "seeking_description": artist.seeking_description,
  "image_link": artist.image_link,
  "past_shows": past_shows, 
  "upcoming_shows": upcoming_shows,
  "past_shows_count": len(past_shows),
  "upcoming_shows_count":len(upcoming_shows),
  }
  return render_template('pages/show_artist.html',artist = data1)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = session.query(Artist).filter_by(id=artist_id).first_or_404()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)

  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form['genres']
  facebook_link = request.form.get('facebook_link')
  try:
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genres = genres
    artist.facebook_link = facebook_link
    session.commit()
  except:
    session_.rollback()
  finally:
    session_.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)

  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form['genres']
  facebook_link = request.form.get('facebook_link')
  try:
    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.genres = genres
    venue.facebook_link = facebook_link
    session.commit()
  except:
    session_.rollback()
  finally:
    session_.close()

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  myForm = request.form
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.getlist('geners')
  facebook_link = request.form.get('facebook_link')

  website_link = request.form.get('website_link')
  image_link = request.form.get('image_link')
  seeking_description = request.form.get('seeking_description')
  if 'seeking_venue' not in request.form:
    seeking_venue = False
  else:
    seeking_venue =True

  try: 
    artist = Artist(seeking_description=seeking_description,seeking_venue=seeking_venue, name = name, city = city, state = state, phone = phone, genres=genres, facebook_link= facebook_link, website_link=website_link,image_link=image_link )
    session_.add(artist)
    session_.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    session_.rollback()
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  finally:
    session_.close()
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = session.query(Artist, Show, Venue).join(Show, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id).all()
  print(data)
  return render_template('pages/shows.html', data=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')
  try:
    show = Show(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
    session_.add(show)
    session_.commit()
    flash('Show was successfully listed!')
  except:
    session_.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    session_.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug= True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
