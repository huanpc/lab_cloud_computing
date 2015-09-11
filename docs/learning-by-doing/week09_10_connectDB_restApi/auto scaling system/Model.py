__author__ = 'huanpc'

import constant
import json
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
        data = dict()
        data['id']=self.id
        data['app_uuid'] = self.app_uuid
        data['name'] =self.name
        data['min_instances'] =self.min_instances
        data['max_instances'] =self.max_instances
        data['enabled'] =self.enabled
        data['locked'] =self.locked
        data['next_time'] =self.next_time
        return json.dumps(data)

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
        data = dict()
        data['id']=self.id
        data['app_uuid'] = self.app_uuid
        data['policy_uuid'] =self.policy_uuid
        data['metric_type'] =self.metric_type
        data['upper_threshold'] =self.upper_threshold
        data['lower_threshold'] =self.lower_threshold
        data['instances_out'] =self.instances_out
        data['instances_in'] =self.instances_in
        data['cooldown_period'] =self.cooldown_period
        data['measurement_period'] =self.measurement_period
        data['deleted'] =self.deleted
        return json.dumps(data)


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
        data = dict()
        data['id']=self.id
        data['app_uuid'] = self.app_uuid
        data['cron_uuid'] =self.name
        data['min_instances'] =self.min_instances
        data['max_instances'] =self.max_instances
        data['enabled'] =self.enabled
        data['cron_string'] =self.cron_string
        data['deleted'] =self.deleted
        return json.dumps(data)


def get_app(name=''):
    '''
    get row in app table
    :param app_uuid:
    :return:
    '''
    result = []
    if name == '':
        for instance in session.query(App).order_by(App.id):
            result.append(instance)
    else:
        result = session.query(App).filter_by(name=name).first()
    return result


def get_policy(policy_uuid=''):
    '''
    get policies in policy table
    :param policy_uuid: if ='' get all
    :return:
    '''
    if policy_uuid == '':
        result = session.query(Policy).order_by(Policy.id)
        return result.all()
    else:
        return session.query(Policy).filter_by(policy_uuid=policy_uuid)

def get_policy_by_app_uuid(app_uuid=''):
    '''

    :param app_name:
    :return:
    '''
    if app_uuid!='':
        result = session.query(Policy).filter_by(app_uuid=app_uuid)
        return result.all()
    return ''

def get_cron(cron_uuid=''):
    '''

    :param cron_uuid: if ='' get all
    :return:
    '''
    if cron_uuid == '':
        result = session.query(Cron).order_by(Cron.id)
        return result.all()
    else:
        return session.query(Cron).filter_by(cron_uuid=cron_uuid)

def get_cron_by_app_uuid(app_uuid=''):
    '''

    :param app_uuid:
    :return:
    '''
    if app_uuid!='':
        result = session.query(Cron).filter_by(app_uuid=app_uuid)
        return result.all()
    return ''
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

def insert_json_data(object,json_data):
    data = object()
    for key in json_data:
        setattr(data,key,data[key])
    return insert(data)
### not done yet
def update(object,name):
    return
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
        if result != None:
            for row in result:
                if row.policy_uuid == object.policy_uuid:
                    return True
    return False


def delete_app(app_name=''):
    '''
    Delete app info by app name
    :param app_name:
    :return:
    '''
    if app_name != '':
        result = session.delete(session.query(App).filter_by(name=app_name))
        session.commit()
    else:
        result = session.delete(session.query(App))
        session.commit()
    return result


def delete_policy(policy_uuid=''):
    '''

    :param policy_uuid:
    :return:
    '''
    if policy_uuid != '':
        session.delete(session.query(Policy).filter_by(policy_uuid=policy_uuid))
        session.commit()
        return True
    else:
        session.delete(session.query(Policy))
        session.commit()
        return True
    return False

def delete_policy_by_app_uuid(app_uuid=''):
    if app_uuid != '':
        session.delete(session.query(Policy).filter_by(app_uuid=app_uuid))
        session.commit()
        return True
    return False
def delete_cron(cron_uuid=''):
    if cron_uuid != '':
        session.delete(session.query(Cron).filter_by(cron_uuid=cron_uuid))
        session.commit()
        return True
    else:
        session.delete(session.query(Cron).filter_by(cron_uuid=cron_uuid))
        session.commit()
        return True
    return False

def delete_cron_by_app_uuid(app_uuid=''):
    if app_uuid != '':
        session.delete(session.query(Cron).filter_by(app_uuid=app_uuid))
        session.commit()
        return True
    return False

def main():
    Base.metadata.create_all(engine)
    app = App(app_uuid=constant.APP_NAME, name=constant.APP_NAME, min_instances=1, max_instances=15, enabled=1,
              locked=0, next_time=0)
    insert(app)
    # print(session.query(App).filter_by(name='demo-server').first())
    cpu_policy = Policy(app_uuid=constant.APP_NAME, policy_uuid='cpu_policy', metric_type=0,
                        upper_threshold=constant.CPU_THRESHOLD_UP, \
                        lower_threshold=constant.CPU_THRESHOLD_DOWN, instances_in=1, instances_out=1, cooldown_period=5,
                        measurement_period=5,
                        deleted=0)
    mem_policy = Policy(app_uuid=constant.APP_NAME, policy_uuid='memory_policy', metric_type=1,
                        upper_threshold=constant.MEM_THRESHOLD_UP, \
                        lower_threshold=constant.MEM_THRESHOLD_DOWN, instances_in=1, instances_out=1, cooldown_period=5,
                        measurement_period=5,
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
