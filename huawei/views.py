import json

from django.http import HttpResponse
from elasticsearch import Elasticsearch

from utils import json_args
# Create your views here.
from utils.mysql_to_es import QAType


def get_round(arg):
    if not isinstance(arg,float):
        arg = float(arg)
    return round(arg, 2)


def num(request):

    rjson = json.dumps({
        "sum": get_round(json_args.sum),
        "count": get_round(json_args.count),
        "time": get_round(json_args.time),
        "qa": get_round(json_args.qa),
        "err": get_round(json_args.err),
        "rate": get_round(json_args.rate),
        "mine": get_round(json_args.mine),
        "pro": get_round(json_args.pro),
        "id": get_round(json_args.id),
    }, )
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(rjson)
    return response


def page_error(request):
    # 全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response


def page_not_found(request):
    # 全局404处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def suggest(request, key_words):
    re_datas = []
    if key_words:
        s = QAType.search()
        s = s.suggest('my_suggest', key_words, completion={
            "field": "suggest", "fuzzy": {
                "fuzziness": 2
            },
            "size": 10
        })
        suggestions = s.execute_suggest()
        for match in suggestions.my_suggest[0].options:
            source = match._source
            re_datas.append(source["question"])
    return HttpResponse(json.dumps(re_datas), content_type="application/json")


def search(request, key_words):
    key_words = str(key_words)
    if key_words.startswith('你好') or key_words.startswith('谢谢') :
        hello_word = """
        很高兴为您服务！我是华为智能客服客服机器人，输入问题点击获取答案或者输入数字0-4，欢迎来聊（撩）～
        0：小猪快跑实验室
        1：郑凯
        2：彭圳生
        3:李爱
        4:刘菲菲
        """
        return HttpResponse(json.dumps(hello_word), content_type="application/json")
    elif key_words.startswith('小猪') or key_words == '0':
        hello_word = """
                小猪快跑实验室坐落于古城西安的一所远近闻名的军事院校，主要研究方向包括智能问答、信息抽取、
                文本挖掘、搜索引擎与自然语言处理等等，非常期待您的加入与合作！
                """
        return HttpResponse(json.dumps(hello_word), content_type="application/json")
    elif key_words.startswith('郑凯') or key_words == '1':
        hello_word = """
        小猪快跑实验室头号小猪，立志成为一名Java攻城狮。
        """
        return HttpResponse(json.dumps(hello_word), content_type="application/json")
    elif key_words.startswith('彭圳生') or key_words == '2':
        hello_word = """
        小猪快跑实验室二号首长，自嗨狂人。
        """
        return HttpResponse(json.dumps(hello_word), content_type="application/json")
    elif key_words.startswith('李爱') or key_words == '3':
        hello_word = """
        小猪快跑实验室头号美女，首长秘书，开玩笑的别当真...
        """
        return HttpResponse(json.dumps(hello_word), content_type="application/json")
    elif key_words.startswith('刘菲菲') or key_words == '4':
        hello_word = """
        小猪快跑实验室猪圈看管人，见证了小猪们的成长。
        """
        return HttpResponse(json.dumps(hello_word), content_type="application/json")

    client = Elasticsearch(hosts=["127.0.0.1"])
    response = client.search(
        index="qa",
        body={
            "query": {
                "multi_match": {
                    "query": key_words,
                    "fields": ["question", "topic"]
                }
            },
            "from": 0,
            "size": 10
        }
    )

    hit_list = []
    for hit in response["hits"]["hits"]:
        hit_dict = {}
        hit_dict["question"] = hit["_source"]["question"]
        hit_dict["topic"] = hit["_source"]["topic"]
        hit_dict["md5"] = hit["_source"]["md5"]
        hit_dict["score"] = hit["_score"]
        hit_dict["answer"] = hit["_source"]["answer"]
        hit_dict["expand"] = hit["_source"]["expand"]

        hit_list.append(hit_dict)

    if key_words == '' or not hit_list:
        hello_word = """
        恭喜！您发现了一片知识知识的荒原，进入后台piggrush.cn添加您想要的问题和答案，点击“信息检索”拓展知识库！
        帐号:test
        密码:test123456
        """
        return HttpResponse(json.dumps(hello_word), content_type="application/json")

    return HttpResponse(json.dumps(hit_list), content_type="application/json")
