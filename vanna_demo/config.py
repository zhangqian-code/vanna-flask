import os
from pathlib import Path


from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(dotenv_path=find_dotenv(), override=True)  # read local .env file

class MyConfig:
    # def __init__(self):
    #     self.init()

    # def init(self):
    #     path = Path(".")
    #     ROOT_DIR = path.parent.absolute()

    #     self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    #     self.db_host: str = os.getenv("DB_HOST", "localhost")
    #     self.db_name: str = os.getenv("DB_NAME", "")
    #     self.db_pass: str = os.getenv("DB_PASS", "")
    #     self.db_user: str = os.getenv("DB_USER", "")
    #     self.db_port: str = os.getenv("DB_PORT", "5432")
    #     self.chroma_path = f"{ROOT_DIR}/chromadb_data/"
    #     self.root_dir = ROOT_DIR


# my_config = MyConfig()


    def __init__(self, db_info=None):
        self.init(db_info)


    def init(self, db_info):
        path = Path(".")
        ROOT_DIR = path.parent.absolute()
        self.db_host: str = db_info.get("host", "localhost")
        self.db_name: str = db_info.get("dbname", "")
        self.db_pass: str = db_info.get("password", "")
        self.db_user: str = db_info.get("user", "")
        self.db_port: str = db_info.get("port", "5432")
        self.chroma_path = f"{ROOT_DIR}/chromadb_data/"
        self.root_dir = ROOT_DIR

# 在这里传入数据源信息
data_source_info = {
    "data": {
        "host": "192.168.0.127",
        "dbname": "dg2-plus-deploy",
        "user": "newcloud",
        "password": "xzkingdeejava",
        "port": "5432",
    }
}
my_config = MyConfig(db_info=data_source_info["data"])

