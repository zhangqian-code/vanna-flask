from vanna.chromadb import ChromaDB_VectorStore
# from vanna.openai import OpenAI_Chat
# from vanna.ollama import Ollama
from vanna.ZhipuAI import ZhipuAI_Chat

from vanna_demo.config import my_config


##################openAI

# class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
#     def __init__(self, config, chroma_config=None):
#         ChromaDB_VectorStore.__init__(self, config=chroma_config)
#         OpenAI_Chat.__init__(self, config={ 'api_key': config.openai_api_key })

# vn = MyVanna(my_config, dict(path=my_config.chroma_path))

##################Ollama
# class MyVanna(ChromaDB_VectorStore, Ollama):
#     def __init__(self, config, chroma_config=None):
#         ChromaDB_VectorStore.__init__(self, config=chroma_config)
#         Ollama.__init__(self, config={ 'model': 'qwen2:latest','ollama_host':'http://localhost:11434' })

# vn = MyVanna(my_config, dict(path=my_config.chroma_path))

##################ZhipuAI
class MyVanna(ChromaDB_VectorStore, ZhipuAI_Chat):
    def __init__(self, config, chroma_config=None):
        ChromaDB_VectorStore.__init__(self, config=chroma_config)
        # ZhipuAI_Chat.__init__(self, config={  'api_key': '2bd2ac274bf4ab3dc467c58f4d25df02.YSfGTL1sym9QYtrO' })
        ZhipuAI_Chat.__init__(self, config={ 'model':'glm-4-plus', 'api_key': '2bd2ac274bf4ab3dc467c58f4d25df02.YSfGTL1sym9QYtrO' })



vn = MyVanna(my_config, dict(path=my_config.chroma_path))


vn.connect_to_postgres(
    host=my_config.db_host,
    dbname=my_config.db_name,
    user=my_config.db_user,
    password=my_config.db_pass,
    port=my_config.db_port,
)
print("7777777777"+my_config.db_name)
