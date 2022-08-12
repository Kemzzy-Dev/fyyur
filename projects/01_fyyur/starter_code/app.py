#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database    

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(300), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(6), default=False, nullable=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(300), nullable=False)#Remember to migrate for this to work
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(6), default=False, nullable=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(30), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
      

#----------------------------------------------------------------------------#
# Filters
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  venues = Venue.query.order_by(db.desc(Venue.id)).limit(10)
  artists = Artist.query.order_by(db.desc(Artist.id)).limit(10)
  return render_template('pages/home.html', venues=venues, artists=artists)

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  get_all_data = Venue.query.all()
  data = []
  for venue in get_all_data:
    area = Venue.query.filter_by(city=venue.city, state=venue.state)
    venues =[]
    for place in area:
      address = {
        'id': place.id,
        'name':place.name,
      }
      venues.append(address)

    areas_list = {
      'city':venue.city,
      'state': venue.state,
      'venues':venues,
    }
    if areas_list not in data:
      data.append(areas_list)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term')
  response = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term)))
  count = response.count()
  return render_template('pages/search_venues.html', results=response,search_word = search_term, count=count)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.get(venue_id)
  genres = data.genres.split(' ')#splitting the string data from the db into lists

  upcoming_shows = []
  past_shows = []
  for show in data.shows:
    if show.date >= str(datetime.now()):
      upcoming_shows.insert(0, show)
    else:
      past_shows.insert(0, show)
  past_shows_count=len(past_shows)
  upcoming_shows_count=len(upcoming_shows)

  
  return render_template('pages/show_venue.html', venue=data, past_shows=past_shows, genres=genres, upcoming_shows=upcoming_shows, upcoming_shows_count=upcoming_shows_count, past_shows_count=past_shows_count)

#  Create Venue
#  ----------------------------------------------------------------

#Don't touch
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertion
      form = VenueForm()

      #Get all the fields from the form 
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone']
      genres = ' '.join(request.form.getlist('genres'))#Gets the value of the genres as a list and converts it to a string
      facebook_link = request.form['facebook_link']
      image_link = request.form['image_link']
      website_link = request.form['website_link']
      seeking_talent = request.form.get("seeking_talent", False)
      seeking_description  = request.form['seeking_description']

      try:
        venues = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_description=seeking_description, seeking_talent=seeking_talent)
        db.session.add(venues)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + name + ' was successfully listed!')
        return redirect(url_for('index'))
      except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        flash('An error occurred. Venue ' + name + ' could not be listed.')
        return redirect(url_for('index'))
      finally:
        db.session.close()

@app.route('/venues/<int:venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
      #Displays a page to ask the user for confirmation before deleting
      venue = Venue.query.get(venue_id)
      return render_template('pages/delete_venue.html', venue=venue)

@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue_form(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  venue = Venue.query.get(venue_id)
  db.session.delete(venue)
  try:
    db.session.commit()
    flash('Venue ' + venue.name + 'was deleted successfully!')
    return redirect(url_for('index'))
  except:
    db.session.rollback()
    flash('Venue ' + venue.name + 'failed to be deleted')
    return redirect(url_for('index'))
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  #The button was implemented

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term')
  response = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term)))
  count = response.count()
  
  return render_template('pages/search_artists.html', results=response, search_word=search_term, count=count)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  data = Artist.query.get(artist_id)
  genres = data.genres.split(' ')#To split the string from the db to lists 

  upcoming_shows = []
  past_shows = []
  for show in data.shows:
    if show.date >= str(datetime.now()):
      upcoming_shows.insert(0, show)
    else:
      past_shows.insert(0, show)
  past_shows_count=len(past_shows)
  upcoming_shows_count=len(upcoming_shows)
  
  return render_template('pages/show_artist.html', artist=data, upcoming_shows=upcoming_shows, genres=genres, past_shows=past_shows, past_shows_count=past_shows_count,upcoming_shows_count=upcoming_shows_count )

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.city.data = artist.city
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.image_link.data = artist.image_link
  form.state.data = artist.state
  form.seeking_description.data = artist.seeking_description
  form.seeking_venue.data = artist.seeking_venue

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)

  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = ' '.join(request.form.getlist('genres'))
  artist.facebook_link = request.form['facebook_link']
  artist.image_link = request.form['image_link']
  artist.website_link = request.form['website_link']
  artist.seeking_venue= request.form.get("seeking_venue", False)
  artist.seeking_description  = request.form['seeking_description']

  try:
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + artist.name + ' was successfully updated!')
    return redirect(url_for('index'))
  except: 
    # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be updated.')
    return redirect(url_for('indes'))
  finally:
    db.session.close()

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.city.data = venue.city
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.image_link.data = venue.image_link
  form.state.data = venue.state
  form.seeking_description.data = venue.seeking_description
  form.seeking_talent.data = venue.seeking_talent
  form.address.data = venue.address
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)

  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.genres = ' '.join(request.form.getlist('genres'))
  venue.facebook_link = request.form['facebook_link']
  venue.image_link = request.form['image_link']
  venue.website_link = request.form['website_link']
  venue.seeking_talent = request.form.get("seeking_talent", False)
  venue.seeking_description  = request.form['seeking_description']

  try:
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + venue.name + ' was successfully updated!')
    return redirect(url_for('index'))
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
    return redirect(url_for('index'))
  finally:
    db.session.close()

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = ' '.join(request.form.getlist('genres'))
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website_link = request.form['website_link']
  seeking_venue= request.form.get("seeking_venue", False)
  seeking_description  = request.form['seeking_description']

  try:
    artists = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_description=seeking_description, seeking_venue=seeking_venue)
    db.session.add(artists)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + name + ' was successfully listed!')
    return render_template('pages/home.html')
  except: 
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    db.session.rollback()
    flash('An error occurred. Artist ' + name + ' could not be listed.')
    return render_template('pages/home.html')
  finally:
    db.session.close()

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = Show.query.all()
 
  return render_template('pages/shows.html', shows=data)

#DO NOT TOUCH
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # #request.form.get('artist_id')
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  date = request.form.get('start_time')

  try:
    shows=Show(artist_id=artist_id, venue_id=venue_id, date=date)
    db.session.add(shows)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    flash('Show was not listed!')
    return render_template('pages/home.html')
  finally:
    db.session.close()

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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
