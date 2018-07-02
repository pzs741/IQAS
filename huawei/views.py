import json

from django.http import HttpResponse
from django.shortcuts import render
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


    if not hit_list:
        hit_list = [
            {"question":"小猪快跑实验室的后台没有答案？","topic":"小猪快跑实验室","md5":"0","score":100.0,"answer":" <ul> <li>登录http://piggrush.cn/，帐号：test，密码：test123456;</li> <li>在主页面的添加数据中补全信息，而后保存;</li> <li> 选择问答信息，信息检索下拉菜单，检索生成，点击确定按钮，等待生成新的搜索建议字段。 </li> <li> 打开APP输入您添加的问题，进行测试。 </li> </ul> ",
             "expand":"[]"},
            {"question": "小猪快跑实验室如何创建得名？", "topic": "小猪快跑实验室", "md5": "1", "score": 75.0, "answer": " <h4> 小猪快跑实验室 </h4> <p> 诞生于 <strong> 第六届中国软件杯大学生软件设计大赛 </strong> ，得名于老队员 <strong> 高志强 </strong> ， 参赛题目 <strong> 分布式爬虫系统 </strong> ，参赛队员 <strong> 王贇 </strong> 、 <strong> 彭圳生 </strong> 和 <strong> 高志强 </strong> ，指导老师 <strong> 李咏 </strong> 。 </p> ",
             "expand": "[]"},
            {"question": "小猪快跑实验室的LOGO含意是什么？", "topic": "小猪快跑实验室", "md5": "2", "score": 50.0, "answer": "<img src='https://raw.githubusercontent.com/pzs741/pzs741.github.io/master/photos/pig'> <hr> <a href='https://raw.githubusercontent.com/pzs741/pzs741.github.io/master/photos/pig'> LOGO </a> 由老队长王贇设计，蕴意笨鸟先飞，小猪快跑，不忘初心，继续前进！",
            "expand": "[]"},
            {"question": "小猪快跑实验室的成员有哪些？", "topic": "小猪快跑实验室", "md5": "3", "score": 25.0, "answer": " <ul> <li> 队长：郑凯 </li> <li> 队员：彭圳生，李爱 </li> <li> 指导老师：刘菲菲 </li> </ul> ",
             "expand": "[]"},
        ]

    return HttpResponse(json.dumps(hit_list), content_type="application/json")

def test(request):
    return render(request,"test.html")
