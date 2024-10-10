from dotenv import load_dotenv
load_dotenv()

from functools import wraps
from flask import Flask, jsonify, Response, request, redirect, url_for
import flask
import os
import requests
import psycopg2
from cache import MemoryCache

app = Flask(__name__, static_url_path='')
# SETUP
cache = MemoryCache()

from vanna.remote import VannaDefault
from vanna_demo.train import train
from vanna_demo.my_vanna import vn
from vanna_demo.config import my_config
from vanna_demo.cryputil import CryptUtil




@app.route('/api/v0/init', methods=['POST'])
def get_data_source():
    # 从请求中获取数据模型 ID
    model_id = flask.request.json.get('modelId')
    
    # 连接 PostgreSQL 数据库
    try:
        # 1.连接平台库
        conn = psycopg2.connect(
            dbname='dg2-plus-deploy',
            user='newcloud',  # 请替换为实际的数据库用户名
            password='xzkingdeejava',  # 请替换为实际的数据库密码
            host='192.168.0.127',
            port='5432'
        )
        cursor = conn.cursor()


        # 2.查询模型信息，构建document
        query = "SELECT * FROM analysis.analysis_model WHERE id = %s"
        cursor.execute(query, (model_id,))
        result = cursor.fetchone()
        
        columns = [desc[0] for desc in cursor.description]
        analysis_model_info = dict(zip(columns, result))
        data_source_id = analysis_model_info.get("data_source_code")
        querySql = analysis_model_info.get("query_sql")
        train_document = f"当前模型的表关联关系如下：{querySql}"

       
        # 查询数据源信息
        query = "SELECT * FROM analysis.dir_link_metadata WHERE id = %s"
        cursor.execute(query, (data_source_id,))
        result = cursor.fetchone()

        if result is None:
            return jsonify({"type": "error", "error": "Data source not found"}), 404

        # 将查询结果映射到字典
        columns = [desc[0] for desc in cursor.description]
        data_source_info = dict(zip(columns, result))


        dataSourceSchema = data_source_info.get("data").get("dataSourceSchema")
        # 3.查询字段信息，构建DDL
        query = "SELECT * FROM analysis.analysis_model_field WHERE model_id = %s"
        cursor.execute(query, (model_id,))
        result = cursor.fetchall()
        ddl_with_comments = generate_create_table_ddl_with_comments(result, dataSourceSchema)

        
        print("密码解密：：：：：：：：：：：：：：：：：：：：：：：：："+CryptUtil.aes_decrypt_1(data_source_info.get("data").get("password")))
        # 当前数据模型所在的数据源信息
        db_info = {
            "host": data_source_info.get("data").get("host"),
            "dbname": data_source_info.get("data").get("dbName"),  # 从 JSON 中提取 dbName
            "user": data_source_info.get("data").get("userName"),  # 从 JSON 中提取 userName
            "password": CryptUtil.aes_decrypt_1(data_source_info.get("data").get("password")),
            # "password": 'xzkingdeejava',
            "port": data_source_info.get("data").get("port"),
        }
        # 初始化当前模型的数据源信息
        my_config.init(db_info)
        # 删除训练数据
        response = requests.post('http://localhost:5000/api/v0/remove_training_data_all', json={})
        
        if response.json().get('success'):
            print("delete all trains data success !!!")
        else:
            # 处理删除失败的情况
            return jsonify({"type": "error", "error": f"Failed to remove training data with id"})
        
        # 添加训练数据
        train(ddl=ddl_with_comments, documentation=train_document)

        return jsonify({"success": True, "message": "Configuration updated successfully", "ddl": ddl_with_comments,"documentation":train_document})

    except Exception as e:
        return jsonify({"type": "error", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



def generate_create_table_ddl_with_comments(result, dataSourceSchema):
    # 数据类型映射
    data_type_mapping = {
        'STRING': 'VARCHAR(255)',
        'NUMBER': 'NUMERIC',
        'DATE': 'TIMESTAMP',
        'int4': 'INT',
        'varchar': 'VARCHAR(255)',
        'timestamp': 'TIMESTAMP',
        'numeric': 'NUMERIC'
    }

    # 初始化用于存储表结构的字典，按表名分组
    tables = {}
    comments = []

    # 遍历查询结果
    for row in result:
        table_name = row[3]  # 表名
        field_name = row[5]  # 字段名称
        raw_field_type = row[11]  # 原始字段类型
        field_description = row[4]  # 字段中文描述

        # 映射数据类型
        field_type = data_type_mapping.get(raw_field_type, 'VARCHAR(255)')  # 默认类型为VARCHAR(255)

        # 如果表名不存在于字典中，初始化一个新列表
        if table_name not in tables:
            tables[table_name] = []

        # 将字段添加到对应表名的列表中
        tables[table_name].append(f"{field_name} {field_type}")

        # 生成字段注释的SQL
        qualified_table_name = f"{dataSourceSchema}.{table_name}"
        comments.append(f"COMMENT ON COLUMN {qualified_table_name}.{field_name} IS '{field_description}';")

    # 用于存储所有表的 DDL 语句
    ddl_statements = []

    # 遍历每个表，生成 CREATE TABLE 语句
    for table_name, columns in tables.items():
        qualified_table_name = f"{dataSourceSchema}.{table_name}"
        create_table_sql = f"CREATE TABLE {qualified_table_name} (\n" + ",\n".join(columns) + "\n);"
        ddl_statements.append(create_table_sql)

    # 拼接创建表的DDL和注释的SQL语句
    return "\n\n".join(ddl_statements) + "\n\n" + "\n".join(comments)






# NO NEED TO CHANGE ANYTHING BELOW THIS LINE
def requires_cache(fields):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            id = request.args.get('id')

            if id is None:
                return jsonify({"type": "error", "error": "No id provided"})
            
            for field in fields:
                if cache.get(id=id, field=field) is None:
                    return jsonify({"type": "error", "error": f"No {field} found"})
            
            field_values = {field: cache.get(id=id, field=field) for field in fields}
            
            # Add the id to the field_values
            field_values['id'] = id

            return f(*args, **field_values, **kwargs)
        return decorated
    return decorator

@app.route('/api/v0/generate_questions', methods=['GET'])
def generate_questions():
    return jsonify({
        "type": "question_list", 
        "questions": vn.generate_questions(),
        "header": "Here are some questions you can ask:"
        })

@app.route('/api/v0/generate_sql', methods=['GET'])
def generate_sql():
    question = flask.request.args.get('question')

    if question is None:
        return jsonify({"type": "error", "error": "No question provided"})

    id = cache.generate_id(question=question)
    sql = vn.generate_sql(question=question)

    cache.set(id=id, field='question', value=question)
    cache.set(id=id, field='sql', value=sql)

    return jsonify(
        {
            "type": "sql", 
            "id": id,
            "text": sql,
        })

@app.route('/api/v0/run_sql', methods=['GET'])
@requires_cache(['sql'])
def run_sql(id: str, sql: str):
    try:
        df = vn.run_sql(sql=sql)

        cache.set(id=id, field='df', value=df)

        return jsonify(
            {
                "type": "df", 
                "id": id,
                "df": df.head(10).to_json(orient='records'),
            })

    except Exception as e:
        return jsonify({"type": "error", "error": str(e)})

@app.route('/api/v0/download_csv', methods=['GET'])
@requires_cache(['df'])
def download_csv(id: str, df):
    csv = df.to_csv()

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 f"attachment; filename={id}.csv"})

@app.route('/api/v0/generate_plotly_figure', methods=['GET'])
@requires_cache(['df', 'question', 'sql'])
def generate_plotly_figure(id: str, df, question, sql):
    try:
        code = vn.generate_plotly_code(question=question, sql=sql, df_metadata=f"Running df.dtypes gives:\n {df.dtypes}")
        fig = vn.get_plotly_figure(plotly_code=code, df=df, dark_mode=False)
        fig_json = fig.to_json()

        cache.set(id=id, field='fig_json', value=fig_json)

        return jsonify(
            {
                "type": "plotly_figure", 
                "id": id,
                "fig": fig_json,
            })
    except Exception as e:
        # Print the stack trace
        import traceback
        traceback.print_exc()

        return jsonify({"type": "error", "error": str(e)})

@app.route('/api/v0/get_training_data', methods=['GET'])
def get_training_data():
    df = vn.get_training_data()
    print("-----------------"+df.id)
    return jsonify(
    {
        "type": "df", 
        "id": "training_data",
        "df": df.head(25).to_json(orient='records'),
    })


import requests  # 需要导入 requests 库

@app.route('/api/v0/remove_training_data_all', methods=['POST'])
def remove_training_data_all():
    # 获取所有训练数据
    training_data = vn.get_training_data()

    if training_data.empty:
        return jsonify({"success": True, "message": "No training data to delete"})

    # 提取训练数据中的 ID 列
    ids = training_data['id'].tolist()

    print("ids--------" + str(ids))

    # 删除计数
    deleted_count = 0

    # 循环删除每一条训练数据
    for id in ids:
        # 使用 requests.post 发送 HTTP 请求到删除接口
        response = requests.post('http://localhost:5000/api/v0/remove_training_data', json={"id": id})
        
        if response.json().get('success'):
            deleted_count += 1
        else:
            # 处理删除失败的情况
            return jsonify({"type": "error", "error": f"Failed to remove training data with id: {id}"})

    return jsonify({"success": True, "message": f"Successfully deleted {deleted_count} records"})



def remove_training_data(id=None):
    # 如果没有传入 id，返回错误
    if id is None:
        return jsonify({"type": "error", "error": "No id provided"})

    # 调用 vn.remove_training_data(id=id) 来删除训练数据
    if vn.remove_training_data(id=id):
        return jsonify({"success": True})
    else:
        return jsonify({"type": "error", "error": "Couldn't remove training data"})



@app.route('/api/v0/remove_training_data', methods=['POST'])
def remove_training_data():
    # Get id from the JSON body
    id = flask.request.json.get('id')

    if id is None:
        return jsonify({"type": "error", "error": "No id provided"})

    if vn.remove_training_data(id=id):
        return jsonify({"success": True})
    else:
        return jsonify({"type": "error", "error": "Couldn't remove training data"})

@app.route('/api/v0/train', methods=['POST'])
def add_training_data():
    question = flask.request.json.get('question')
    sql = flask.request.json.get('sql')
    ddl = flask.request.json.get('ddl')
    documentation = flask.request.json.get('documentation')

    try:
        id = vn.train(question=question, sql=sql, ddl=ddl, documentation=documentation)

        return jsonify({"id": id})
    except Exception as e:
        print("TRAINING ERROR", e)
        return jsonify({"type": "error", "error": str(e)})

@app.route('/api/v0/generate_followup_questions', methods=['GET'])
@requires_cache(['df', 'question', 'sql'])
def generate_followup_questions(id: str, df, question, sql):
    followup_questions = vn.generate_followup_questions(question=question, sql=sql, df=df)

    cache.set(id=id, field='followup_questions', value=followup_questions)

    return jsonify(
        {
            "type": "question_list", 
            "id": id,
            "questions": followup_questions,
            "header": "Here are some followup questions you can ask:"
        })

@app.route('/api/v0/load_question', methods=['GET'])
@requires_cache(['question', 'sql', 'df', 'fig_json', 'followup_questions'])
def load_question(id: str, question, sql, df, fig_json, followup_questions):
    try:
        return jsonify(
            {
                "type": "question_cache", 
                "id": id,
                "question": question,
                "sql": sql,
                "df": df.head(10).to_json(orient='records'),
                "fig": fig_json,
                "followup_questions": followup_questions,
            })

    except Exception as e:
        return jsonify({"type": "error", "error": str(e)})

@app.route('/api/v0/get_question_history', methods=['GET'])
def get_question_history():
    return jsonify({"type": "question_history", "questions": cache.get_all(field_list=['question']) })

@app.route('/')
def root():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
