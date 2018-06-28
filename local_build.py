import hashlib
import os

import MySQLdb
import elasticsearch
from EMDT import EMDT
from QGDT import QGDT

from utils.mysql_to_es import es, QAType, getConnect, MySQLQueryPagination


def get_md5(question):
    m = hashlib.md5(question.encode("utf-8"))
    return m.hexdigest()


def summery(summery_list):
    summery = []
    question_list = []
    for i in summery_list:
        q = QGDT(i[0],
                 LOG_ENABLE=True,
                 LOG_LEVEL='WARNING',
                 MAX_SAMPLE=10,
                 RANDOM=True,
                 LAMBDA=0.2,
                 ALPHA=0.3,
                 BETA=0.5)
        q.ranking_algorithm()
        question_list.append(q.question_generation())
    for index, i in enumerate(summery_list):
        question = question_list[index]
        topic = i[1]
        answer = i[2]
        expand_list = []
        for i in question_list:
            if i == question:
                pass
            else:
                expand_list.append(i)
        summery.append([question, topic, answer, expand_list])
    return summery


class Mysql(object):
    def __init__(self, i):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'root', 'QADB', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        self.question = i[0]
        self.md5 = get_md5(self.question)
        self.topic = i[1]
        self.answer = i[2]
        self.file_name = path
        self.expand = str(i[3])

    def save(self):
        insert_sql = """
                    insert into huawei_qamodel(md5, question, topic, answer,file_name,expand)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
        self.cursor.execute(insert_sql, (self.md5, self.question, self.topic, self.answer, self.file_name, self.expand))
        insert_sql = """
                            insert into huawei_uploadmodel(file_name,file_path)
                            VALUES (%s, %s)
                        """
        self.cursor.execute(insert_sql, (self.file_name, 'huawei/'+self.file_name))
        self.conn.commit()


def mysql_to_es():
    # es初始化
    es.indices.delete(index='qa', ignore=[400, 404])
    QAType.init()
    # mysql初始化
    conn = getConnect()
    pag = MySQLQueryPagination(conn)
    sql = r'SELECT * FROM `huawei_qamodel` WHERE id<%s'
    # mysql_to_elasticsearch
    for ret in pag.queryForList(sql):
        actions = []
        for row in ret:
            try:
                action = pag._parse_serialize_table_data(row)
                actions.append(action)
            except Exception as e:
                print(e)
        elasticsearch.helpers.bulk(es, actions)
        del actions[0:len(actions)]
    conn.close()

if __name__ == "__main__":
    dir = os.path.dirname(os.getcwd()) + '/IQAS/media/huawei'
    path_list = os.listdir(dir)
    for path in path_list:
        filepath = os.path.join(dir, path)
        with open(filepath, 'r', encoding='utf-8') as html:
            i = html.read()
            e = EMDT(i,
                     LOG_ENABLE=False,
                     LOG_LEVEL='WARNING',
                     FORMAT='%(asctime)s - %(levelname)s - %(message)s',
                     BLOCKSIZE=10,
                     CAPACITY=5,
                     TIMEOUT=5,
                     SAVEIMAGE=False,
                     CONTENT_RULE=['.help-details.webhelp', '.help-center-title'],
                     TOPIC_RULE=['.crumbs', '.parentlink'],
                     QA_JACCARD_THRESHOLD=0.25,
                     REMOVE_HTML=False,
                     )
            e.analyse()
            e.format()
            summery_list = summery(e.summery)
            for i in summery_list:
                m = Mysql(i)
                try:
                    m.save()
                    print('md5:{}\nquestion:{}\ntopic:{}\nanswer:{}\nfile_name:{}\nexpand:{}\n'.format(m.md5, m.question, m.topic, m.answer,m.file_name,m.expand))
                except Exception as e:
                    print(e)
    mysql_to_es()