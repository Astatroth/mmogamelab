from mg import *
from mg.core.auth import User

class ConstructorProject(Module):
    "This is the main module of every project. It must load very fast"
    def register(self):
        Module.register(self)
        self.rdep(["mg.core.web.Web"])
        self.rhook("web.setup_design", self.web_setup_design)
        self.rhook("project.title", self.project_title)

    def child_modules(self):
        lst = ["mg.core.auth.Sessions", "mg.core.auth.Interface", "mg.admin.AdminInterface", "mg.core.cluster.Cluster", "mg.core.emails.Email", "mg.core.queue.Queue", "mg.core.cass_maintenance.CassandraMaintenance", "mg.admin.wizards.Wizards", "mg.constructor.project.ConstructorProjectAdmin", "mg.constructor.ConstructorUtils", "mg.constructor.domains.Domains", "mg.socio.Socio", "mg.constructor.players.Auth"]
        if self.app().project.get("admin_confirmed"):
            lst.extend(["mg.constructor.design.DesignMod", "mg.constructor.game.Game", "mg.constructor.interface.Dynamic", "mg.constructor.interface.Interface", "mg.game.money.Money",
                "mg.constructor.realplexor.Realplexor", "mg.constructor.chat.Chat"])
        return lst

    def project_title(self):
        return self.app().project.get("title_short", "New Game")

    def web_setup_design(self, vars):
        req = self.req()
        if vars.get("global_html"):
            return
        #if req.group == "admin":
        vars["global_html"] = "constructor/admin_global.html"

class ConstructorProjectAdmin(Module):
    def register(self):
        Module.register(self)
        self.rhook("menu-admin-top.list", self.menu_top_list, priority=10)
        self.rhook("ext-admin-project.destroy", self.project_destroy, priv="project.admin")
        self.rhook("permissions.list", self.permissions_list)
        self.rhook("forum-admin.init-categories", self.forum_init_categories)
        self.rhook("menu-admin-root.index", self.menu_root_index, priority=-1000000)

    def menu_root_index(self, menu):
        a = [menu]
        req = self.req()
        project = self.app().project
        if not project.get("admin_confirmed"):
            if project.get("domain") and req.has_access("project.admin"):
                admin = self.obj(User, req.user())
                project.set("admin_confirmed", admin.uuid)
                project.store()
                self.call("project.admin_confirmed", admin)
                self.call("cluster.appconfig_changed")
                self.call("web.redirect", "/admin")
            menu[:] = [ent for ent in menu if ent.get("leaf")]

    def menu_top_list(self, topmenu):
        req = self.req()
        if self.app().project.get("inactive") and req.has_access("project.admin"):
            topmenu.append({"href": "/admin-project/destroy", "text": self._("Destroy this game"), "tooltip": self._("You can destroy your game while not created")})

    def project_destroy(self):
        if self.app().project.get("inactive"):
            self.main_app().hooks.call("project.cleanup", self.app().project.uuid)
        self.call("web.redirect", "http://www.%s/cabinet" % self.app().inst.config["main_host"])

    def permissions_list(self, perms):
        perms.append({"id": "project.admin", "name": self._("Project main administrator")})

    def forum_init_categories(self, cats):
        cats.append({"id": uuid4().hex, "topcat": self._("Game"), "title": self._("News"), "description": self._("Game news published by the administrators"), "order": 10.0, "default_subscribe": True})
        cats.append({"id": uuid4().hex, "topcat": self._("Game"), "title": self._("Game"), "description": self._("Talks about game activities: gameplay, news, wars, politics etc."), "order": 20.0})
        cats.append({"id": uuid4().hex, "topcat": self._("Game"), "title": self._("Newbies"), "description": self._("Dear newbies, if you have any questions about the game, feel free to ask"), "order": 30.0})
        cats.append({"id": uuid4().hex, "topcat": self._("Game"), "title": self._("Diplomacy"), "description": self._("Authorized guild members can talk to each other about diplomacy and politics issues here"), "order": 40.0})
        cats.append({"id": uuid4().hex, "topcat": self._("Admin"), "title": self._("Admin talks"), "description": self._("Discussions with the game administrators. Here you can discuss any issues related to the game itself."), "order": 50.0})
        cats.append({"id": uuid4().hex, "topcat": self._("Admin"), "title": self._("Reference manuals"), "description": self._("Actual reference documents about the game are placed here."), "order": 60.0})
        cats.append({"id": uuid4().hex, "topcat": self._("Admin"), "title": self._("Bug reports"), "description": self._("Report any problems in the game here"), "order": 70.0})
        cats.append({"id": uuid4().hex, "topcat": self._("Reallife"), "title": self._("Smoking room"), "description": self._("Everything not related to the game: humor, forum games, hobbies, sport etc."), "order": 80.0})
        cats.append({"id": uuid4().hex, "topcat": self._("Reallife"), "title": self._("Art"), "description": self._("Poems, prose, pictures, photos, music about the game"), "order": 90.0})
        cats.append({"id": uuid4().hex, "topcat": self._("Trading"), "title": self._("Services"), "description": self._("Any game services: mercenaries, guardians, builders etc."), "order": 100.0})
        cats.append({"id": uuid4().hex, "topcat": self._("Trading"), "title": self._("Market"), "description": self._("Market place to sell and by any item"), "order": 110.0})
