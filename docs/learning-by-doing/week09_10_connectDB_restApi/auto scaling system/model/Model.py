__author__ = 'huanpc'

import config
import json
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import \
    BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
    DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
    LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
    NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
    TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR

#engine = create_engine('mysql+pymysql://'+config['username']+':'+config['password']+'@'+config['host']+':'+config['port']+'/'+config['dbname'], echo=True)
engine = create_engine(config.MODEL_ENGINE, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()


class App(Base):
    __tablename__ = 'apps'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    app_uuid = Column(VARCHAR(255), unique=True)
    name = Column(VARCHAR(255))
    min_instances = Column(SMALLINT(unsigned=True))
    max_instances = Column(SMALLINT(unsigned=True))
    enabled = Column(TINYINT(unsigned=True))
    locked = Column(TINYINT(unsigned=True))
    next_time = Column(INTEGER(unsigned=True))
    policies = relationship("Policy", order_by="Policy.id", backref="app", cascade="all, delete, delete-orphan")
    crons = relationship("Cron", order_by="Cron.id", backref="app", cascade="all, delete, delete-orphan")

    @staticmethod
    def __get(self):
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

    def __repr__(self):
        return self.__get(self)

class Policy(Base):
    __tablename__ = 'policies'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    app_uuid = Column(VARCHAR(255), ForeignKey('apps.app_uuid'))
    policy_uuid = Column(VARCHAR(255), unique=True)
    metric_type = Column(TINYINT(unsigned=True))
    upper_threshold = Column(FLOAT)
    lower_threshold = Column(FLOAT)
    instances_out = Column(SMALLINT(unsigned=True))
    instances_in = Column(SMALLINT(unsigned=True))
    cooldown_period = Column(SMALLINT(unsigned=True))
    measurement_period = Column(SMALLINT(unsigned=True))
    deleted = Column(TINYINT(unsigned=True))

    @staticmethod
    def __get(self):
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

    def __repr__(self):
        return self.__get(self)


class Cron(Base):

    __tablename__ = 'crons'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    app_uuid = Column(VARCHAR(255), ForeignKey('apps.app_uuid'))
    cron_uuid = Column(VARCHAR(255),unique=True)
    min_instances = Column(SMALLINT(unsigned=True))
    max_instances = Column(SMALLINT(unsigned=True))
    cron_string = Column(VARCHAR(255))
    deleted = Column(TINYINT(unsigned=True))


    @staticmethod
    def __get(self):
        data = dict()
        data['id']=self.id
        data['app_uuid'] = self.app_uuid
        data['cron_uuid'] =self.cron_uuid
        data['min_instances'] =self.min_instances
        data['max_instances'] =self.max_instances
        data['enabled'] =self.enabled
        data['cron_string'] =self.cron_string
        data['deleted'] =self.deleted
        return json.dumps(data)

    def __repr__(self):
        return self.__get(self)


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
        result = session.query(Policy).filter_by(policy_uuid=policy_uuid)
        return result.all()

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
    '''

    :param object:
    :param json_data:
    :return:
    '''
    data = object(**json_data)
    return insert(data)

#
def update(object,app_name,json_data):
    '''

    :param app_name:
    :param json_data:
    :return:
    '''
    app = session.query(App).filter_by(app_name=app_name).first()
    if isinstance(object,App):
        update_app(app_name,json_data)
    elif isinstance(object,Policy):
        update_policy(app.policies,json_data)
    return True
#
def update_app(app_name,json_data):
    '''

    :param app_name:
    :param json_data:
    :return:
    '''
    session.query(App).filter_by(app_name=app_name).update(json_data)
    session.commit()
    return True

def update_policy(policy_uuid,json_data):
    '''

    :param policy_uuid:
    :param json_data:
    :return:
    '''
    session.query(Policy).filter_by(policy_uuid=policy_uuid).update(json_data)
    session.commit()
    return True

def update_cron(cron_uuid,json_data):
    '''

    :param cron_uuid:
    :param json_data:
    :return:
    '''
    session.query(Cron).filter_by(cron_uuid=cron_uuid).update(json_data)
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
        apps = session.query(App).filter_by(name=app_name)
        try:
            for app in apps:
                session.delete(app)
                session.commit()
        except:
            session.rollback()
    else:
        try:
            session.query(App).delete()
            session.commit()
        except:
            session.rollback()
    return True


def delete_policy(policy_uuid=''):
    '''

    :param policy_uuid:
    :return:
    '''
    if policy_uuid != '':
        policies = session.query(Policy).filter_by(policy_uuid=policy_uuid)
        try:
            for policy in policies:
                result = session.delete(policy)
            session.commit()
            return True
        except:
            session.rollback()
    else:
        try:
            session.query(Policy).delete()
            session.commit()
            return True
        except:
            session.rollback()
    return False

def delete_policy_by_app_uuid(app_uuid=''):
    if app_uuid != '':
        try:
            policies = session.query(Policy).filter_by(app_uuid=app_uuid)
            for policy in policies:
                session.delete(policy)
                session.commit()
            return True
        except:
            session.rollback()
    return False
def delete_cron(cron_uuid=''):
    if cron_uuid != '':
        crons = session.query(Cron).filter_by(cron_uuid=cron_uuid)
        try:
            for cron in crons:
                session.delete(cron)
                session.commit()
            return True
        except:
            session.rollback()
    else:
        try:
            session.query(Cron).delete()
            session.commit()
            return True
        except:
                session.rollback()
    return False

def delete_cron_by_app_uuid(app_uuid=''):
    if app_uuid != '':
        crons = session.query(Cron).filter_by(app_uuid=app_uuid)
        try:
            for cron in crons:
                session.delete(cron)
                session.commit()
            return True
        except:
            session.rollback()
    return False

# def main():
#     Base.metadata.create_all(engine)
#     app = App(app_uuid=constant.APP_NAME, name=constant.APP_NAME, min_instances=1, max_instances=15, enabled=1,
#               locked=0, next_time=0)
#     insert(app)
#     # print(session.query(App).filter_by(name='demo-server').first())
#     cpu_policy = Policy(app_uuid=constant.APP_NAME, policy_uuid='cpu_policy', metric_type=0,
#                         upper_threshold=constant.CPU_THRESHOLD_UP, \
#                         lower_threshold=constant.CPU_THRESHOLD_DOWN, instances_in=1, instances_out=1, cooldown_period=5,
#                         measurement_period=5,
#                         deleted=0)
#     mem_policy = Policy(app_uuid=constant.APP_NAME, policy_uuid='memory_policy', metric_type=1,
#                         upper_threshold=constant.MEM_THRESHOLD_UP, \
#                         lower_threshold=constant.MEM_THRESHOLD_DOWN, instances_in=1, instances_out=1, cooldown_period=5,
#                         measurement_period=5,
#                         deleted=0)
#     insert(cpu_policy)
#     insert(mem_policy)
    # for i in range(2,5):
    #     session.delete(session.query(Policy).filter_by(id=i).one())
    # session.delete(session.query(Policy).filter_by(id=8).one())
    # session.commit()
    policies = get_policy()
    # app = get_app()
    # print(app)

# if __name__ == '__main__':
#     main()
