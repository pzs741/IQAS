from datetime import datetime

import elasticsearch.helpers
from elasticsearch_dsl import DocType, Completion, Keyword, Text
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections

from utils import json_args

# -------------------------------ES parameter------------------------------------------
es = connections.create_connection(hosts=["localhost"])


def gen_suggests(index, info_tuple):
    # 根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        new_words = set()
        if text:
            # 调用ed的analyzer接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter': ["lowercase"]},
                                       body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = anylyzed_words - used_words

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class QAType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    question = Text(analyzer="ik_max_word")
    url = Keyword()
    url_object_id = Keyword()
    topic = Keyword()
    answer = Text(analyzer="ik_max_word")
    expand = Text()

    class Meta:
        index = "qa"
        doc_type = "huawei"


import MySQLdb

# ----------------------------MYSQL parameter-----------------------------------------
strHost = '127.0.0.1'
strDB = 'QADB'
strUser = 'root'
strPasswd = 'root'
table = 'huawei_qamodel'
fixnum = 1000000


def seEncode(ustr):
    # 负责把入数据库的字符串，转化成utf-8编码
    if ustr is None:
        return ''
    else:
        return str(ustr, encoding='utf-8')


# connect to DB
def getConnect(db=strDB, host=strHost, user=strUser, passwd=strPasswd, charset="utf8"):
    return MySQLdb.connect(host=strHost, db=strDB, user=strUser, passwd=strPasswd, charset="utf8")


def initClientEncode(conn):
    # mysql client encoding=utf8
    curs = conn.cursor()
    curs.execute("SET NAMES utf8")
    conn.commit()
    return curs


class MySQLQueryPagination(object):
    def __init__(self, conn, numPerPage=50000):
        self.conn = conn
        self.numPerPage = numPerPage

    def queryForList(self, sql):
        totalPageNum = int(self.__calTotalPages(sql))
        # print totalPageNum
        for pageIndex in range(totalPageNum):
            yield self.__queryEachPage(sql, pageIndex)

    def __createPaginaionQuerySql(self, sql, currentPageIndex):
        startIndex = self.__calStartIndex(currentPageIndex)
        qSql = r'select * from %s limit %s,%s' % (table, startIndex, self.numPerPage)
        # print qSql
        return qSql

    def __queryEachPage(self, sql, currentPageIndex):
        curs = initClientEncode(self.conn)
        qSql = self.__createPaginaionQuerySql(sql, currentPageIndex)
        curs.execute(qSql)
        result = curs.fetchall()
        curs.close()
        return result

    def __calStartIndex(self, currentPageIndex):
        startIndex = currentPageIndex * self.numPerPage
        return startIndex

    def __calTotalRowsNum(self, sql):
        # 计算总行数
        tSql = r'select count(*) from ' + table
        curs = initClientEncode(self.conn)
        curs.execute(tSql)
        result = curs.fetchone()
        curs.close()
        totalRowsNum = 0
        if result != None:
            totalRowsNum = int(result[0])
            return totalRowsNum

    def __calTotalPages(self, sql):
        # 计算总页数
        totalRowsNum = 0
        if fixnum > 0:
            totalRowsNum = fixnum
        else:
            totalRowsNum = self.__calTotalRowsNum(sql)
            totalPages = 0
        if (totalRowsNum % self.numPerPage) == 0:
            totalPages = totalRowsNum / self.numPerPage
        else:
            totalPages = (totalRowsNum / self.numPerPage) + 1
        return totalPages

    def __calLastIndex(self, totalRows, totalPages, currentPageIndex):
        # 计算结束时候的索引
        lastIndex = 0
        if totalRows < self.numPerPage:
            lastIndex = totalRows
        elif ((totalRows % self.numPerPage == 0)
              or (totalRows % self.numPerPage != 0 and currentPageIndex < totalPages)):
            lastIndex = currentPageIndex * self.numPerPage
        elif (totalRows % self.numPerPage != 0 and currentPageIndex == totalPages):  # 最后一页
            lastIndex = totalRows
        return lastIndex

    def _parse_serialize_table_data(self, row):
        # 解析序列化表数据
        md5 = row[0]
        question = row[1]
        topic = row[2]
        answer = row[3]
        expand = row[4]
        suggest = gen_suggests(QAType._doc_type.index, ((question, 7), (topic, 3)))
        action = {
            '_op_type': 'index',
            '_index': 'qa',
            '_type': 'huawei',
            '_source': {
                "md5": md5,
                "question": question,
                "topic": topic,
                "answer": answer,
                "expand": expand,
                'suggest': suggest
            }
        }
        return action


def mysql_to_es():
    # es初始化
    es.indices.delete(index='qa', ignore=[400, 404])
    QAType.init()
    # mysql初始化
    conn = getConnect()
    pag = MySQLQueryPagination(conn)
    sql = r'SELECT * FROM `huawei_qamodel` WHERE id<%s'
    # init json_args
    start_time = datetime.now()
    # mysql_to_elasticsearch
    for ret in pag.queryForList(sql):
        if ret:
            json_args.sum = len(ret)
            json_args.id += 1
        actions = []
        for row in ret:
            try:
                action = pag._parse_serialize_table_data(row)
                actions.append(action)
                end_time = datetime.now()
                last_seconds = (end_time - start_time).total_seconds()
                json_args.time = last_seconds / 60
                json_args.count += 1
                json_args.rate = ((json_args.count - json_args.err) / json_args.count) * 100
                json_args.pro = ((json_args.count + json_args.err) / json_args.sum) * 100
            except:
                end_time = datetime.now()
                last_seconds = (end_time - start_time).total_seconds()
                json_args.time = last_seconds / 60
                json_args.err += 1
                json_args.rate = ((json_args.count - json_args.err) / json_args.count) * 100
                json_args.pro = ((json_args.count + json_args.err) / json_args.sum) * 100
        elasticsearch.helpers.bulk(es, actions)
        del actions[0:len(actions)]
    conn.close()


if __name__ == "__main__":
    pass
