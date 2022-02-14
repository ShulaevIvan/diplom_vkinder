import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json

database = 'postgresql://vkinder:dnweapons1513@localhost:5432/vkinder_db'  #параметры базы данных(Заменить на свои)
Base = declarative_base()
engine = sq.create_engine(database)
Session = sessionmaker(bind=engine)
session = Session()


class VkinderUser(Base):
    
    __tablename__ = 'vkinder_user'
    
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)
    user_name = sq.Column(sq.String)
    age = sq.Column(sq.String)

class TargetUser(Base):
    
    __tablename__ = 'users'
    
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)
    user_name = sq.Column(sq.String)
    id_User = sq.Column(sq.Integer, sq.ForeignKey('vkinder_user.id'))
    user = relationship(VkinderUser)

def create_tables():
    
    Base.metadata.create_all(engine)

def add_user(user):
    
    session.expire_on_commit = False
    session.add(user)
    session.commit()

def view_all(user_id):
    
    links = []
    q = session.query(TargetUser)
    
    for i in q:
        links.append(i.vk_id)
        
    return links

def write_master():
    
    create_tables()
    
    with open('output.json', 'r', encoding='utf8') as f:
        
        data = json.load(f)
        
        for i in data[0]['people']:
            
            create_tables()
            user = VkinderUser(vk_id=i['vk_id'], user_name=i['user_name'],
                        age=i['age'])
            add_user(user)

        for i in data[0]['favorite']:
            
            searching_user = TargetUser(vk_id=i['vk_id'], user_name=i['user_name'],
                                        id_User=user.id)
            add_user(searching_user)

