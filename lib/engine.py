from sqlalchemy import create_engine

# 连接数据库的 URL
db_url = 'mysql://root:12345678@localhost:3306/nba'

# 创建数据库引擎
engine = create_engine(db_url)

# 如果需要，还可以添加其他与数据库相关的配置，例如连接池大小、连接超时等。
