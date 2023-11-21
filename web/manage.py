from flask.cli import FlaskGroup
from app import app, db
from werkzeug.security import generate_password_hash
from app.models.authuser import AuthUser
from app.models.art import Art
from app.models.favourite_art import FavouriteArt

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    # pass
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    # pass
    db.session.add(AuthUser(email="c@c.com", name='Raphael',
                            password=generate_password_hash('1234',
                                                            method='sha256'),
                            avatar_url='https://ui-avatars.com/api/?name=Raphael&background=83ee03&color=fff'))
    db.session.add(AuthUser(email="a@a.com", name='Isaac',
                            password=generate_password_hash('1234',
                                                            method='sha256'),
                            avatar_url='https://ui-avatars.com/api/?name=Isaac&background=83ee03&color=fff'))
    db.session.commit()
    # db.session.add(Art(title="The School of Athens", price=2000, detail="The School of Athens (Italian: Scuola di Atene) is a fresco by the Italian Renaissance artist Raphael. The fresco was painted between 1509 and 1511 as a part of Raphael's commission to decorate the rooms now known as the Stanze di Raffaello, in the Apostolic Palace in the Vatican. It depicts a congregation of philosophers, mathematicians, and scientists from Ancient Greece, including Plato, Aristotle, Pythagoras, Archimedes, and Heraclitus. The Italian artists Leonardo da Vinci and Michelangelo are also featured in the painting, shown as Plato and Heraclitus respectively.", img_url="The_School_of_Athens__by_Raffaello_Sanzio_da_Urbino.jpg", type=8,user_id=2))
    # db.session.commit()
    # db.session.add(FavouriteArt(art_id=1, user_id=2))
    # db.session.commit()

if __name__ == "__main__":
    cli()

