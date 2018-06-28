import time
from datetime import datetime

import xadmin
from utils import json_args
from utils.mysql_to_es import mysql_to_es
from xadmin import views
from .models import UploadModel, QAModel

def json_init():
    json_args.time = 0.0
    json_args.count = 0.0
    json_args.sum = 0.0
    json_args.qa = 0.0
    json_args.err = 0.0
    json_args.rate = 0.0
    json_args.mine = 0.0
    json_args.pro = 0.0
    json_args.id = 0.0
    return

class UploadAdmin(object):
    import_excel = True
    list_display = ['file_name', 'file_path']
    search_fields = ['file_name', 'file_path']
    list_filter = ['file_name', 'file_path']
    refresh_times = [1, 3, 5, 10]
    json_init()
    def post(self, request, *args, **kwargs):
        start_time = datetime.now()
        if 'html' in request.FILES:
            files = request.FILES.getlist('html')
            json_args.sum = len(files)
            for i in files:
                try:
                    u = UploadModel()
                    u.file_name = i.name
                    u.file_path = i
                    u.save()
                    end_time = datetime.now()
                    last_seconds = (end_time - start_time).total_seconds()
                    json_args.time = last_seconds / 60.0
                    json_args.count += 1.0
                    json_args.rate = ((json_args.count - json_args.err) / json_args.count) * 100
                    json_args.mine = (json_args.qa / json_args.count) * 100
                    json_args.pro = ((json_args.count + json_args.err) / json_args.sum) * 100
                except:
                    end_time = datetime.now()
                    last_seconds = (end_time - start_time).total_seconds()
                    json_args.time = last_seconds / 60.0
                    json_args.err += 1.0
                    json_args.rate = ((json_args.count - json_args.err) / json_args.count) * 100
                    json_args.mine = (json_args.qa / json_args.count) * 100
                    json_args.pro = ((json_args.count + json_args.err) / json_args.sum) * 100
        time.sleep(1.5)
        json_init()
        return super(UploadAdmin, self).post(request, json_args, kwargs)


class QA_Admin(object):
    import_ie = True
    list_display = ['md5', 'question', 'topic', 'answer', 'expand', 'file_name']
    search_fields = ['md5', 'question', 'topic', 'answer', 'expand', 'file_name']
    list_filter = ['md5', 'question', 'topic', 'answer', 'expand', 'file_name']
    list_editable = ['question', 'topic', 'answer', 'expand']
    refresh_times = [1, 3, 5, 10]

    def post(self, request, *args, **kwargs):
        json_init()
        mysql_to_es()
        time.sleep(1.5)
        json_init()
        return super(QA_Admin, self).post(request, args, kwargs)


class GlobalsETTINGS(object):
    site_title = '智能问答后台管理系统'
    site_footer = '2018 小猪快跑实验室 粤ICP备18061360号'


xadmin.site.register(QAModel, QA_Admin)
xadmin.site.register(UploadModel, UploadAdmin)
xadmin.site.register(views.CommAdminView, GlobalsETTINGS)
