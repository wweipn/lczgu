from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker


# 创建连接
engine = create_engine('mysql+pymysql://wuweipeng:Wuweipeng997@192.168.1.10:3306/test_lczgu_shop_member',
                       encoding='utf-8')
# 生成orm基类
Base = declarative_base()


class User(Base):  # User继承了上述的操作

    __tablename__ = 'es_red_package'
    id = Column(Integer, primary_key=True)
    member_id = Column(String(32))
    money = Column(String(32))
    available_money = Column(Integer)
    create_time = Column(Integer)
    type = Column(String(64))


# 执行上述的操作
Base.metadata.create_all(engine)
Session_class = sessionmaker(bind=engine)  # 进行数据库的连接
Session = Session_class()  # 生成session 实例

# 查询单条数据
data1 = Session.query(User).filter(User.money > 0).first()
print(data1.member_id, data1.money)

# 查询多行数据,并遍历查询出来的结果
data2 = Session.query(User).filter(User.money > 0).all()
for i in data2:
    print(i.member_id, i.money, type(i.member_id), type(i.money))

# 多条件查询
data3 = Session.query(User).filter(User.money > 0).filter(User.id > 1).first()
print(data3)
