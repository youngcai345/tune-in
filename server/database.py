from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from sqlalchemy import join
from sqlalchemy.orm import aliased
from sqlalchemy import bindparam
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sql
import psycopg2

SERVER = 'localhost:5432'
DATABASE = 'test'
USERNAME = 'postgres'
PASSWORD = 'Invincible31'
DATABASE_CONNECTION = f'postgresql+psycopg2://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}'

class Database():
    #create DB connection string with user:pw@server/dbname
    engine = sql.create_engine(DATABASE_CONNECTION)

    def __init__(self):
        #establishes connection when this database class is created wherever used.
        self.connection = self.engine.connect()
        print("Database Instance created")

    def fetchByQuery(self, query):
        fetchQuery = self.connection.execute(f"SELECT * FROM {query}")
        for data in fetchQuery.fetchall():
            print(data)

    def userExistsInTable(self, user_id, table):
        session = Session(bind=self.connection)
        return len(session.query(table).filter(table.user_id == user_id).all()) > 0

    def displayUserData(self, user_id, table):
        session = Session(bind=self.connection)
        result = session.query(table).filter(table.user_id == user_id)
        for row in result:
            print ("rank:",row.rank, "URI: ",row.spotify_uri)
    
    def fetchAllUsersInTable(self, table):
        session = Session(bind=self.connection)
        users = session.query(table).all()
        for user in users:
            print(user)

    def saveUserData(self, entries):
        session = Session(bind=self.connection)
        session.bulk_save_objects(entries)
        session.commit()

    def deleteUserData(self, user_id, table):
        session = Session(bind=self.connection)
        result = session.query(table).filter(table.user_id == user_id)
        result.delete()
        session.commit()

    # def updateUserData(self, entries, table): 
    #     session = Session(bind=self.connection)
    #     statement = table.__table__.update().where(table.user_id == bindparam('b_user_id')).where(table.rank == bindparam('b_rank')).values(spotify_uri=bindparam('b_spotify_uri'))
    #     session.execute(statement, entries)
    #     session.commit()

    def getShared(self, user_list, table):  # RANKSUM BABYYYY
        """
        Returns list of shared objects between n users.

        Parameters:
            user_list: list of user ids
            table: Track or Artist

        Returns:
            List containing lists of spotify uris and individual ranks sorted by their sum
        """
        session = Session(bind=self.connection)
        user_data = [] # list of queries
        for user_id in user_list:
            user_data.append(session.query(table).filter(table.user_id == user_id))

        shared_data = {}
        for user in user_data:
            for row in user:
                uri = row.spotify_uri
                rank = row.rank
                if uri in shared_data:
                    shared_data[uri].append(rank)
                else:
                    shared_data[uri] = [rank]

        for uri in shared_data:
            missing = len(user_list) - len(shared_data[uri]) 
            shared_data[uri] += [100] * missing 
        
        ordered_data = [[uri, ranks] for uri, ranks in sorted(shared_data.items(), key=lambda item: sum(item[1]))]
        print(ordered_data)
        return ordered_data

    def getSeeds(self, shared_data, k):
        # Returns first k spotify uris in shared data list
        return [item[0] for item in shared_data[:k]]

Base = declarative_base()

class TopArtists(Base):
    """Model for top artists table."""
    __tablename__ = 'artists'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    spotify_uri = Column(String)
    rank = Column(Integer)

    def __repr__(self):
        return "<Artist(user_id='%s', spotify_uri='%s', rank='%s')>" % (self.user_id, self.spotify_uri, self.rank)

class TopTracks(Base):
    """Model for top tracks table."""
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    spotify_uri = Column(String)
    rank = Column(Integer)

    def __repr__(self):
        return "<Track(user_id='%s', spotify_uri='%s', rank='%s')>" % (self.user_id, self.spotify_uri, self.rank)
