import os
import hashlib
from utils import json_args
from EMDT import EMDT
from QGDT import QGDT

# Definit your method here.
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
                 MAX_SAMPLE=3,
                 RANDOM=True,
                 LAMBDA=0.2,
                 ALPHA=0.3,
                 BETA=0.5)
        q.ranking_algorithm()
        question_list.append(q.question_generation())
    for index,i in enumerate(summery_list):
        question = question_list[index]
        topic = i[1]
        answer = i[2]
        expand_list = []
        for i in question_list:
            if i == question:
                pass
            else:
                expand_list.append(i)
        summery.append([question,topic,answer,expand_list])
    return summery

def initfile(filename):
    filepath = os.path.join(MEDIA_ROOT, filename)
    with open(filepath, 'r', encoding='utf-8') as html:
        i = html.read()
        e = EMDT(i,
                 LOG_ENABLE=True,
                 LOG_LEVEL='INFO',
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
            qa = QAModel()
            qa.question = i[0]
            qa.md5 = get_md5(qa.question)
            qa.topic = i[1]
            qa.answer = i[2]
            qa.file_name = filename
            qa.expand = i[3]
            qa.save()
            json_args.qa += 1.0


# Create your models here.
from django.db import models
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from IQAS.settings import MEDIA_ROOT
from django.utils.encoding import force_text

# 类对象会对应数据库中的一个表
class QAModel(models.Model):
    #CharField对应数据库的varchar类型
    md5 = models.CharField(max_length=50,verbose_name='id',primary_key=True)
    question = models.CharField(max_length=150,verbose_name='问题')
    topic = models.CharField(max_length=32,verbose_name='主题')
    answer = models.TextField(verbose_name='答案')
    expand = models.TextField(verbose_name='拓展问题')
    file_name = models.CharField(max_length=255, verbose_name='文件名')



    #重新定义一些属性
    class Meta:
        #表的别名
        verbose_name = '问答信息'
        #此项不定义则别名后会存在字符s（英文框架造成的）
        verbose_name_plural = verbose_name


class MyStorge(FileSystemStorage):
    #删除重复上传的文件
    def get_available_name(self, name, max_length=None):
        filepath = os.path.join(MEDIA_ROOT,name)
        if self.exists(name):
            os.remove(filepath)
        return name

    #初始化文件生成QA对并保存
    def save(self, name, content, max_length=None):
        """
        Save new content to the file specified by name. The content should be
        a proper File object or any python file-like object, ready to be read
        from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name

        if not hasattr(content, 'chunks'):
            content = File(content, name)

        name = self.get_available_name(name, max_length=max_length)
        name = self._save(name,content)
        initfile(name)
        return force_text(name.replace('\\','/'))


class UploadModel(models.Model):
    file_name = models.CharField(max_length=255, verbose_name='文件名',primary_key=True)
    file_path = models.FileField(upload_to='huawei',verbose_name='存储路径',storage=MyStorge())


    # 重新定义一些属性
    class Meta:
        # 表的别名
        verbose_name = '文件上传'
        # 此项不定义则别名后会存在字符s（英文框架造成的）
        verbose_name_plural = verbose_name


