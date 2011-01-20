import mg
from mg import *
import re

re_valid_docfile = re.compile(r'^[a-z0-9\-]+(/[a-z0-9\-]+)*/?$')
re_not_found = re.compile(r'^file error - .*: not found$')
re_doc_tag = re.compile(r'^\s*<!--\s*doc\.([a-z_]+)\s+(.*?)\s*-->\s*(.*)', re.DOTALL)

class Documentation(Module):
    def register(self):
        Module.register(self)

        self.rhook("ext-doc.index", self.index)
        self.rhook("ext-doc.handler", self.handler)

    def index(self):
        req = self.req()
        req.args = "index"
        return self.handler()

    def handler(self):
        req = self.req()
        m = re_valid_docfile.match(req.args)
        if not m:
            self.call("web.not_found")
        lang = self.call("l10n.lang")
        vars = {
            "lang": lang,
            "htmlmeta": {}
        }
        try:
            content = self.call("web.parse_template", "constructor/docs/%s/%s.html" % (lang, req.args), vars)
        except TemplateException as e:
            if re_not_found.match(str(e)):
                self.call("web.not_found")
            else:
                raise
        while True:
            m = re_doc_tag.search(content)
            if not m:
                break
            tag, value, content = m.group(1, 2, 3)
            if tag == "keywords" or tag == "description":
                vars["htmlmeta"][tag] = value
            else:
                vars[tag] = value
        menu = []
        while vars.get("parent"):
            try:
                with open("%s/templates/constructor/docs/%s/%s.html" % (mg.__path__[0], lang, vars["parent"])) as f:
                    v = {}
                    for line in f:
                        m = re_doc_tag.search(line)
                        if not m:
                            break
                        tag, value = m.group(1, 2)
                        v[tag] = value
                    if v.get("short_title"):
                        menu.insert(0, {"href": "/doc/%s" % vars["parent"], "html": v["short_title"]})
                    elif v.get("title"):
                        menu.insert(0, {"href": "/doc/%s" % vars["parent"], "html": v["title"]})
                    vars["parent"] = v.get("parent")
            except IOError:
                vars["parent"] = None
        if len(menu):
            menu.append({"html": vars.get("short_title", vars.get("title"))})
            menu[-1]["lst"] = True
            vars["menu_left"] = menu
        self.call("web.response_global", '<div class="doc-content">%s</div>' % content, vars)
