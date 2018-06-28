# coding:utf-8

import xadmin
from xadmin.views import BaseAdminPlugin, ListAdminView
from django.template import loader


#elasticsearch 导入
class ListImportIEPlugin(BaseAdminPlugin):
    import_ie = False

    def init_request(self, *args, **kwargs):
        return bool(self.import_ie)

    def block_top_toolbar(self, context, nodes):
        context = context.dicts[1]
        nodes.append(loader.render_to_string('xadmin/ie/model_list.top_toolbar.import.html',context=context))


xadmin.site.register_plugin(ListImportIEPlugin, ListAdminView)