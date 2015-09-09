__author__ = 'huanpc'
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import \
        BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
        DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
        LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
        NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
        TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR

engine = create_engine('mysql+pymysql://root:autoscaling@secret@127.0.0.1:3306/policydb',echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()
class app(Base):
    __tablename__ = 'apps'

    id = Column(INTEGER,primary_key=True,autoincrement=True)
    app_uuid = Column(VARCHAR(255))
    name = Column(VARCHAR(255))
    min_instances = Column(SMALLINT(unsigned=True))
    max_instances = Column(SMALLINT(unsigned=True))
    enabled = Column(TINYINT(unsigned=True))
    locked = Column(TINYINT(unsigned=True))
    next_time = Column(INTEGER(unsigned=True))
    def __repr__(self):
        return "<app(name='%s', id='%s', app_uuid='%s')>" % (self.name, self.id, self.app_uuid)