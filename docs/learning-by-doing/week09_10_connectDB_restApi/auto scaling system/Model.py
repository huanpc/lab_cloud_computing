__author__ = 'huanpc'
import constant
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import \
    BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
    DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
    LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
    NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
    TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR

engine = create_engine('mysql+pymysql://root:autoscaling@secret@127.0.0.1:3306/policydb', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()


class App(Base):
    __tablename__ = 'apps'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    app_uuid = Column(VARCHAR(255))
    name = Column(VARCHAR(255))
    min_instances = Column(SMALLINT(unsigned=True))
    max_instances = Column(SMALLINT(unsigned=True))
    enabled = Column(TINYINT(unsigned=True))
    locked = Column(TINYINT(unsigned=True))
    next_time = Column(INTEGER(unsigned=True))

    def __repr__(self):
        return "<app(name='%s', id='%s', app_uuid='%s', min_instances='%s', max_instances='%s')>" \
               % (self.name, self.id, self.app_uuid, self.min_instances, self.max_instances)


class Policy(Base):
    __tablename__ = 'policies'
    # Id INT AUTO_INCREMENT PRIMARY KEY, \
    # app_uuid VARCHAR(255), \
    # policy_uuid VARCHAR(255), \
    # metric_type TINYINT UNSIGNED, \
    # upper_threshold FLOAT, \
    # lower_threshold FLOAT, \
    # instances_out SMALLINT UNSIGNED, \
    # instances_in SMALLINT UNSIGNED, \
    # cooldown_period SMALLINT UNSIGNED, \
    # measurement_period SMALLINT UNSIGNED, \
    # deleted TINYINT UNSIGNED \
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    app_uuid = Column(VARCHAR(255))
    policy_uuid = Column(VARCHAR(255))
    metric_type = Column(TINYINT(unsigned=True))
    upper_threshold = Column(FLOAT)
    lower_threshold = Column(FLOAT)
    instances_out = Column(SMALLINT(unsigned=True))
    instances_in = Column(SMALLINT(unsigned=True))
    cooldown_period = Column(SMALLINT(unsigned=True))
    measurement_period = Column(SMALLINT(unsigned=True))
    deleted = Column(TINYINT(unsigned=True))

    def __repr__(self):
        return "<policies(id='%s', app_uuid='%s', policy_uuid='%s')>" % (self.id, self.app_uuid, self.policy_uuid)


class Cron(Base):
    __tablename__ = 'crons'
    # Id INT AUTO_INCREMENT PRIMARY KEY, \
    # app_uuid VARCHAR(255), \
    # cron_uuid VARCHAR(255), \
    # min_instances SMALLINT UNSIGNED, \
    # max_instances SMALLINT UNSIGNED, \
    # cron_string VARCHAR(255), \
    # deleted TINYINT UNSIGNED \
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    app_uuid = Column(VARCHAR(255))
    cron_uuid = Column(VARCHAR(255))
    min_instances = Column(SMALLINT(unsigned=True))
    max_instances = Column(SMALLINT(unsigned=True))
    cron_string = Column(VARCHAR(255))
    deleted = Column(TINYINT(unsigned=True))

    def __repr__(self):
        return "<crons(id='%s', app_uuid='%s', cron_uuid='%s')>" % (self.id, self.app_uuid, self.cron_uuid)


def get_app(app_uuid=''):
    '''
    get row in app table
    :param app_uuid:
    :return:
    '''
    result = []
    if app_uuid == '':
        for instance in session.query(App).order_by(App.id):
            result.append(instance)
    else:
        result = session.query(App).filter_by(app_uuid=app_uuid).first()
    return result


def get_policy(app_uuid='',policy_uuid=''):
    '''
    get policies in policy table
    :param app_uuid:
    :param policy_uuid:
    :return:
    '''
    if app_uuid == '':
        result = session.query(Policy).order_by(Policy.id)
        return result.all()
    elif policy_uuid=='':
        result =  session.query(Policy).filter_by(app_uuid=app_uuid)
        return result.all()
    else:
        return session.query(Policy).filter_by(app_uuid=app_uuid,policy_uuid=policy_uuid)

def insert(object):
    '''
    insert object into database
    :param object:
    :return: true - if operation success, false - if object has existed in database
    '''
    if is_exists(object):
        return False
    session.add(object)
    session.commit()
    return True


def is_exists(object):
    '''
    check object is exists in database?
    :param object:
    :return: true - if exists, else false
    '''
    if isinstance(object, App):
        result = get_app(object.app_uuid)
        if result != None:
            return True
    elif isinstance(object, Policy):
        result = get_policy(object.app_uuid)
        if result !=None:
            for row in result:
                if row.policy_uuid == object.policy_uuid:
                    return True
    return False


def main():
    Base.metadata.create_all(engine)
    app =  App(app_uuid=constant.APP_NAME,name=constant.APP_NAME,min_instances=1,max_instances=15,enabled=1,locked=0,next_time=0)
    insert(app)
    # print(session.query(App).filter_by(name='demo-server').first())
    cpu_policy = Policy(app_uuid=constant.APP_NAME, policy_uuid='cpu_policy', metric_type=0, upper_threshold=constant.CPU_THRESHOLD_UP, \
                        lower_threshold=constant.CPU_THRESHOLD_DOWN, instances_in=1, instances_out=1, cooldown_period=5, measurement_period=5,
                        deleted=0)
    mem_policy = Policy(app_uuid=constant.APP_NAME, policy_uuid='memory_policy', metric_type=1, upper_threshold=constant.MEM_THRESHOLD_UP, \
                        lower_threshold=constant.MEM_THRESHOLD_DOWN, instances_in=1, instances_out=1, cooldown_period=5, measurement_period=5,
                        deleted=0)
    insert(cpu_policy)
    insert(mem_policy)
    # for i in range(2,5):
    #     session.delete(session.query(Policy).filter_by(id=i).one())
    # session.delete(session.query(Policy).filter_by(id=8).one())
    # session.commit()
    policies = get_policy()
    app = get_app()
    print(app)


# if __name__ == '__main__':
#     main()
