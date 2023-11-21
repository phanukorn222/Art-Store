from flask import (jsonify, render_template, request, url_for, flash, redirect, Response)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse
from sqlalchemy.sql import text
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.sql.expression import func
from app import app
from app import db
from app import oauth
from app import login_manager
from app import images
from app.forms import forms
from app.models.authuser import AuthUser
from app.models.favourite_art import FavouriteArt
from app.models.art import Art
from app.models.buyer import Buyer
import secrets
import string

art_type = { 1 : 'Oil', 2 : 'Acrylic', 3 : 'Watercolors', 4 : 'Gouache', 5 : 'Pastels', 6 : 'Encaustic', 7 : 'Ink painting', 8 : 'Digital painting', 9 : 'Other' }

@login_manager.user_loader
def load_user(user_id):
    return AuthUser.query.get(int(user_id))

@app.route('/', methods=['GET'])
def index():
    arts = Art.query.filter_by(sold=False).order_by(func.random()).limit(5).all()
    return render_template('index.html', arts=arts)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        password = form.password.data

        user = AuthUser.query.filter_by(email=email).first()

        if user:
            flash('Email address already exists')
            return redirect(url_for('signup'))

        avatar_url = gen_avatar_url(email, name)
        new_user = AuthUser(email=email, name=name,
                            password=generate_password_hash(
                            password, method='sha256'),
                            avatar_url=avatar_url)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data

        user = AuthUser.query.filter_by(email=email).first()
 
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('shop')
        return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/google/')
def google():
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()

    userinfo = token['userinfo']
    email = userinfo['email']
    user = AuthUser.query.filter_by(email=email).first()

    if not user:
        name = userinfo['name']
        random_pass_len = 12
        password = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(random_pass_len))
        picture = userinfo['picture']
        new_user = AuthUser(email=email, name=name,
                           password=generate_password_hash(
                               password, method='sha256'),
                           avatar_url=picture)
        db.session.add(new_user)
        db.session.commit()
        user = AuthUser.query.filter_by(email=email).first()
    login_user(user)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('shop')
    return redirect(next_page)

@app.route('/profile', methods=['GET'], defaults={'user_email': None})
@app.route('/profile/<string:user_email>', methods=['GET'])
def profile(user_email):
    page = request.args.get('page', 1, type=int)
    
    if not user_email:
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.path))
        
        pagination = Art.query.filter_by(user_id=current_user.id, sold=False).paginate(page=page, per_page=12)
        return render_template('profile.html', pagination=pagination, FavouriteArt=FavouriteArt)

    if current_user.is_authenticated:
        if user_email == current_user.email:
            return redirect(url_for('profile'))
    
    page = request.args.get('page', 1, type=int)
    user = AuthUser.query.filter_by(email=user_email).first()

    if not user:
        flash('Profile is not exists.')
        return redirect(url_for('shop'))
    
    pagination = Art.query.filter_by(user_id=user.id, sold=False).paginate(page=page, per_page=12)
    return render_template('profile.html', user=user, pagination=pagination, FavouriteArt=FavouriteArt)

@app.route('/profile/sold', methods=['GET'], defaults={'user_email': None})
@app.route('/profile/<string:user_email>/sold', methods=['GET'])
def profile_inactive(user_email):
    page = request.args.get('page', 1, type=int)

    if not user_email:
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.path))
        
        pagination = Art.query.filter_by(user_id=current_user.id, sold=True).paginate(page=page, per_page=12)
        return render_template('profile.html', user=current_user, pagination=pagination, FavouriteArt=FavouriteArt)
    
    if current_user.is_authenticated:
        if user_email == current_user.email:
            return redirect(url_for('profile_inactive'))
    
    page = request.args.get('page', 1, type=int)
    user = AuthUser.query.filter_by(email=user_email).first()
    if not user:
        flash('Profile is not exists.')
        return redirect(url_for('shop'))
    
    pagination = Art.query.filter_by(user_id=user.id, sold=True).paginate(page=page, per_page=12)
    return render_template('profile.html', user=user, pagination=pagination, FavouriteArt=FavouriteArt)

@app.route('/profile/contacted', methods=['GET'])
@login_required
def profile_contacted():
    page = request.args.get('page', 1, type=int)
    
    pagination = Buyer.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=12)
    return render_template('profile.html', pagination=pagination, FavouriteArt=FavouriteArt)

@app.route('/profile/customer', methods=['GET'])
@login_required
def profile_customer():
    art_objects = []
    arts_query = Art.query.filter_by(user_id=current_user.id, sold=False).all()
    for art in arts_query:
        if art.buyers:
            art_objects.append(art)
    
    return render_template('profile.html', art_objects=art_objects)

@app.route('/profile/setting', methods=['GET', 'POST'])
@login_required
def profile_setting():
    form = forms.ProfileForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        password = form.password.data

        user = AuthUser.query.get(current_user.id)
        if not user or not check_password_hash(user.password, password):
            flash("Please check your password and try again.")
            return redirect(url_for('profile_setting'))
        
        if user.email != email:
            user_email = AuthUser.query.filter_by(email=email).first()
            if user_email:
                flash("Email address already exists.")
                return redirect(url_for('profile_setting'))
            
        avatar_url = None
        if user.email != email or user.name != name: 
            avatar_url = gen_avatar_url(email, name)
        else:
            avatar_url = user.avatar_url

        user.update(name=name, email=email, avatar_url=avatar_url)
        db.session.commit()
    return render_template('setting.html', form=form)

@app.route('/profile/favourite', methods=['GET', 'POST'])
@login_required
def profile_favourite():
    form = forms.FavouriteArtFrom()
    page = request.args.get('page', 1, type=int)

    if form.validate_on_submit():
        id_ = form.art_id.data
    
        art_liked = FavouriteArt.query.filter_by(art_id=id_, user_id=current_user.id).first()
        if not art_liked:
            favourite_art = FavouriteArt(art_id=id_, user_id=current_user.id)
            db.session.add(favourite_art)
        else:
            db.session.delete(art_liked)
        db.session.commit()

        pagination = FavouriteArt.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=12, error_out=False)
        if not pagination.items:
            page = page-1
            pagination = FavouriteArt.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=12, error_out=False)
        count_favourite = FavouriteArt.query.filter_by(art_id=id_).count()
        return jsonify(template=render_template('include/favourite.html', pagination=pagination), page=page, count=count_favourite)

    pagination = FavouriteArt.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=12)
    return render_template('favourite-art.html', pagination=pagination)

@app.route('/shop', methods=['GET', "POST"])
def shop():
    form_search = forms.SearchForm()
    form_filter = forms.FilterForm()
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', None, type=str)
    filter = request.args.get('filter', "0", type=str)

    if form_search.validate_on_submit():
        if search:
            if filter != "0":
                search = "%{}%".format(search)
                user = AuthUser.query.filter(AuthUser.name.ilike(search)).first()            
                if user:
                    pagination = Art.query.filter(Art.title.ilike(search) | (Art.user_id == user.id), Art.sold == False, Art.type==filter).paginate(page=page, per_page=12)
                    return jsonify(template=render_template('include/shop.html', pagination=pagination, FavouriteArt=FavouriteArt))
                else:
                    pagination = Art.query.filter(Art.title.ilike(search), Art.sold == False, Art.type==filter).paginate(page=page, per_page=12)
                    return jsonify(template=render_template('include/shop.html', pagination=pagination, FavouriteArt=FavouriteArt))
            else:
                search = "%{}%".format(search)
                user = AuthUser.query.filter(AuthUser.name.ilike(search)).first()            
                if user:
                    pagination = Art.query.filter(Art.title.ilike(search) | (Art.user_id == user.id), Art.sold == False).paginate(page=page, per_page=12)
                    return jsonify(template=render_template('include/shop.html', pagination=pagination, FavouriteArt=FavouriteArt))
                else:
                    pagination = Art.query.filter(Art.title.ilike(search), Art.sold == False).paginate(page=page, per_page=12)
                    return jsonify(template=render_template('include/shop.html', pagination=pagination, FavouriteArt=FavouriteArt))
        else:
            pagination = Art.query.filter_by(sold=False).paginate(page=page, per_page=12)
            if filter != "0":
                pagination = Art.query.filter(Art.sold == False, Art.type==filter).paginate(page=page, per_page=12)
                return jsonify(template=render_template('include/shop.html', pagination=pagination, FavouriteArt=FavouriteArt))
            else:
                pagination = Art.query.filter(Art.sold == False).paginate(page=page, per_page=12)
                return jsonify(template=render_template('include/shop.html', pagination=pagination, FavouriteArt=FavouriteArt))

    if search:
        if filter != "0":
            search = "%{}%".format(search)
            user = AuthUser.query.filter(AuthUser.name.ilike(search)).first()
            if user:
                pagination = Art.query.filter(Art.title.ilike(search) | (Art.user_id == user.id), Art.sold == False, Art.type==filter).paginate(page=page, per_page=12)
            else:
                pagination = Art.query.filter(Art.title.ilike(search), Art.sold == False, Art.type==filter).paginate(page=page, per_page=12)
        else:
            search = "%{}%".format(search)
            user = AuthUser.query.filter(AuthUser.name.ilike(search)).first()
            if user:
                pagination = Art.query.filter(Art.title.ilike(search) | (Art.user_id == user.id), Art.sold == False).paginate(page=page, per_page=12)
            else:
                pagination = Art.query.filter(Art.title.ilike(search), Art.sold == False).paginate(page=page, per_page=12)
    else:
        if filter != "0":
            pagination = Art.query.filter(Art.sold == False, Art.type==filter).paginate(page=page, per_page=12)
        else:
            pagination = Art.query.filter(Art.sold == False).paginate(page=page, per_page=12)
    return render_template('shop.html', pagination=pagination, FavouriteArt=FavouriteArt, type=art_type, form_search=form_search, form_filter=form_filter)

@app.route('/art/<int:id>', methods=['GET'])
def art(id):
    entry = Art.query.get(id)
    if not entry:
        flash("Entry is not exists.")
        return redirect(url_for('shop'))

    count_favourite = FavouriteArt.query.filter_by(art_id=id).count()
    app.logger.debug(art_type[entry.type])
    if not current_user.is_authenticated:
        return render_template('art.html', art=entry, count_favourite=count_favourite, art_type=art_type, islike=False)
    
    buyer_check = Buyer.query.filter_by(user_id=current_user.id, art_id=entry.id).first()
    if entry.user.id == current_user.id:
        islike = FavouriteArt.query.filter_by(art_id=id,user_id=current_user.id).first()
        if not islike:
            return render_template('art.html', art=entry, count_favourite=count_favourite, art_type=art_type, islike=False, buyer_check=buyer_check, buyers=entry.buyers)
        return render_template('art.html', art=entry, count_favourite=count_favourite, art_type=art_type, islike=True, buyer_check=buyer_check, buyers=entry.buyers)
    else:
        islike = FavouriteArt.query.filter_by(art_id=id,user_id=current_user.id).first()
        if not islike:
            return render_template('art.html', art=entry, count_favourite=count_favourite, art_type=art_type, islike=False, buyer_check=buyer_check, buyers=entry.buyers)
        return render_template('art.html', art=entry, count_favourite=count_favourite, art_type=art_type, islike=True, buyer_check=buyer_check, buyers=entry.buyers)

@app.route('/art/create', methods=['GET', 'POST'])
@login_required
def create_art():
    form = forms.CreateArtForm()
    if form.validate_on_submit():
        title = form.title.data
        price = form.price.data
        type = form.type.data
        detail = form.detail.data
        f = form.image.data
        filename = secure_filename(images.save(f))
        
        post = Art(title=title, price=price, detail=detail, img_url=filename, type=type, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('art', id=post.id))
    return render_template('create.html', form=form)

@app.route('/art/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_art(id):
    entry = Art.query.get(id)
    if not entry:
        flash("Entry is not exists.")
        return redirect(url_for('shop'))

    if entry.sold:
        return redirect(url_for('art', id=id))
    
    form = forms.EditArtForm()
    if form.validate_on_submit():
        title = form.title.data
        price = form.price.data
        type = form.type.data
        detail = form.detail.data
        
        if entry.user_id == current_user.id:
            entry.update(title=title, price=price, type=type, detail=detail)
        db.session.commit()
        return redirect(url_for('art', id=id))
        
    form.type.default = entry.type
    form.detail.default = entry.detail
    form.process()
    return render_template('edit.html', form=form, art=entry, art_type=art_type)

@app.route('/art/<int:id>/delete', methods=['POST'])
@login_required
def delete_art(id):
    try:
        entry = Art.query.get_or_404(id)

        if entry.user_id == current_user.id:
            db.session.delete(entry)
            db.session.commit()
        return Response(status=200)
    except Exception as e:
        return Response(status=500)

@app.route('/art/<int:id>/buy', methods=['POST'])
@login_required
def buy_art(id):
    art = Art.query.get_or_404(id)
    
    if art.sold:
        return jsonify(message="This art is sold."), 406
    
    buyer_check = Buyer.query.filter_by(user_id=current_user.id, art_id=art.id).first()
    if buyer_check:
        return jsonify(message="You are already contacted."), 406
    
    buy = Buyer(art_id=id, user_id=current_user.id)
    db.session.add(buy)
    db.session.commit()
    return jsonify(email=buy.art.user.email)

@app.route('/art/<int:id>/sold', methods=['POST'])
@login_required
def sold_art(id):
    art = Art.query.get_or_404(id)

    if art.sold:
        return jsonify(message="This art is already sold."), 406

    if current_user.id == art.user_id:
        art.update_sold(sold=True)
        db.session.commit()
    return Response(status=200)

def gen_avatar_url(email, name):
    bgcolor = generate_password_hash(email, method='sha256')[-6:]
    color = hex(int('0xffffff', 0) -
                int('0x'+bgcolor, 0)).replace('0x', '')
    lname = ''
    temp = name.split()
    fname = temp[0][0]
    if len(temp) > 1:
        lname = temp[1][0]


    avatar_url = "https://ui-avatars.com/api/?name=" + \
        fname + "+" + lname + "&background=" + \
        bgcolor + "&color=" + color
    return avatar_url