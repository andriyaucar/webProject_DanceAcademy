#-*- coding: utf-8 -*-

import web

urls = (
    '/', 'index',
    '/about', 'about_page',
    '/abouts', 'about_item',
    '/danslar', 'dance_page',
    '/contact', 'contact_page',
    '/contacts', 'contact_item',
    '/picture', 'picture_page',
    '/pictures', 'pictures_item',
    '/team', 'trainer_page',
    '/video', 'videos_page',
    '/videos', 'video_item',
    '/dance/(.*)/(.*)', 'dances_item',
    '/dance/add', 'add_dance',
    '/trainer/add', 'add_trainer',
    '/events', 'event_page'
)

render = web.template.render("templates", base="base")
db = web.database(dbn='mysql',user='ceng3507',pw='1234',db='ceng3507')
team = db.select('team')
print team
team = list(team)
for trainer in team:
  print trainer.name
print team[3].name

menu_items = [ ("/", "Home"), ("/dances", "All Dances"), \
               ("/about", "About"), ("/team", "Trainers"), ("/contact", "Contact") ]

def required(input_str):
   input_str = clean_str(input_str)   
   return input_str != ""            

def clean_str(input_str):
   result = input_str.strip()
   words = result.split()
   words = [ w.capitalize() for w in words ]
   result = " ".join(words)
   return(result)

def is_float(input_str):
  try:
    result = float(input_str)
    return True
  except ValueError:
    return False
    
	   
class index:
    def GET(self):
       return render.index()
   
class dance_page:
    def GET(self):
       dances = db.select("dances")
       team = db.select("team")
       team_dict = {}
       for trainer in team:
         team_dict[trainer.tid] = trainer.name
       print "TEAM: %s" % team_dict
       return render.dances(dances, team_dict)

class trainer_page:
    def GET(self):
       team = list(db.select("team"))
       inp = web.input()
       trainer_dances = []
       trainer = inp.get("trainer",None)
       if trainer != None:
           trainer_name = trainer.replace("+", " ")
           trainer_dances = db.query("SELECT * FROM dances AS d, team AS t WHERE t.name = $trainer_name AND t.tid = d.tid", vars=locals())
       return render.team(team, trainer_dances)
     
    def old_GET(self):
       team = list(db.select("team"))
       inp = web.input()
       trainer_dances = []
       trainer = inp.get("trainer", None)
       if trainer != None:
           trainer_name = trainer.replace("+", " ")
           print "TRAINER NAME : %s" % trainer_name
           for trainer in team:
              if trainer.name == trainer_name:
                 tid = trainer.tid
           print "tid : %s" % tid      
           dances = db.select("dances")
           for dance in dances:       
               if dance.tid == tid:  
                   trainer_dances.append(dance)
       
       print "TRAINER DANCES : %s" % trainer_dances                        
       return render.team(team, trainer_dances)
     
class dances_item:
    def GET(self, dances_name,dances_id): 
       did = int(dances_id)
       print "DID=%d" % did
       dances_item = db.select("dances", where="did=$did", vars=locals())[0]
       tid = dances_item.tid
       trainer = db.select("team", where="tid=$tid", vars=locals())[0]
       img_rows = db.select("photo_img", where="did=$did", vars=locals())
       img_labels = list(db.select("photo"))
       img_dict = {}
       for row in img_labels:
         img_dict[row.pid] = row.img
       img_list = []
       for row in img_rows:
          img_list.append(img_dict[row.pid])
       img_str = ", ".join(img_list)
       from urllib import quote_plus
       return render.dance(dances_item, trainer, quote_plus, img_str) 
	      
class about_page:
    def GET(self):
       about = db.select("about")
       return render.about(about)
   
class about_item:
    def GET(self, member_name, member_id):
       aid = int(member_id)
       print "AID=%d" % aid
       member_item = db.select("about", where="aid=$aid", vers=locals())[0]
       return render.abouts(about_item)
	
class event_page:
    def GET(self):
      return render.events()

class picture_page:
    def GET(self):
       picture = db.select("picture")
       return render.picture(picture)
   
class picture_item:
    def GET(self, picture_name, picture_id):
       hid = int(picture_id)
       print "HID=%d" % hid
       picture_item = db.select("picture", where="hid=$hid", vers=locals())[0]
       return render.pictures(picture_item)

class videos_page:
    def GET(self):
       video = db.select("video")
       return render.video(video)
	   
class video_item:
    def GET(self, video_name, video_id):
       vid = int(video_id)
       print "VID=%d" % vid
       video_item = db.select("video", where="vid=$vid", vers=locals())[0]
       return render.videos(video_item)
	   
class contact_page:
    def GET(self):
       contact = db.select("contact")
       return render.contact(contact)
   
class contact_item:
    def GET(self, contact_name, contact_id):
       cid = int(contact_id)
       print "CID=%d" % cid
       contact_item = db.select("contact", where="cid=$cid", vers=locals())[0]
       return render.contacts(contact_item)
	   
	   
class add_trainer:

    def check_trainer(name):
       trainer_rows = list(db.select("team"))
       trainer_names = [ a.name for a in trainer_rows]
       name = clean_str(name)
       return not name in trainer_names

    login = web.form.Form( 
          web.form.Textbox('name', 
             web.form.Validator('Can not be empty', required),
             web.form.Validator('Trainer already exist', check_trainer),
             size=15,
             description="Trainer Name"),           
    )
    
           
    def GET(self):   
        form = self.login()
        return render.trainer_add(form.render())

    def POST(self):         
        form = self.login() 
        if not form.validates():
            form.name.value = clean_str(form.name.value)
            return render.trainer_add(form.render())
        else:    
            inp = web.input()
            db.insert('team', name=inp.get("name"))                        
            raise web.seeother('/team')
      
class add_dance:
    
    trainer_rows = list(db.select("team"))
    team = [ (row.tid, row.name) for row in trainer_rows ]
    required_field = web.form.Validator('Can not be empty', required)
    photo_rows = list(db.select("photo"))
    photo = [ (row.pid, row.img) for row in photo_rows ]
    
	
    def check_trainer_dances(inp):
      tid = inp.tid
      title = clean_str(inp.title)
      trainer_dance_rows = db.query("SELECT d.title FROM dances AS d WHERE d.tid = $tid", vars=locals())
      trainer_dance_titles = [ row.title for row in trainer_dance_rows ]
      return title not in trainer_dance_titles
    
    dance_add_form = web.form.Form( 
      web.form.Textbox('title', required_field, description="Title"),
      web.form.Textarea('summary', required_field, rows="5", cols="20", description="Summary"),
      web.form.Dropdown('tid', team, description="Trainer"),  
      validators = [ web.form.Validator("The dance available", check_trainer_dances) ]                                      
    )
    def form_manual(self, form, validate):
       inp = web.input(img=[])
       photo = inp.get("img")
       form_html = form.render()
       form_html = form_html[0:-8]
       form_html += u'<tr><th><label for="img">Type</label></th><td>'
       for (pid,name) in self.photo:
          if str(pid) in photo:
             form_html += u'<input type="checkbox" value=%d name="img" checked=true>%s' % (pid,name)  
          else:
             form_html += u'<input type="checkbox" value=%d name="img">%s' % (pid,name)  
       if photo == [] and validate:
           form_html += u"<br><strong class='wrong'>Can not be empty!</strong>"   
       form_html += u'</td></tr>'
       form_html += u'<tr><th><label for="img">Image</label></th><td>'
       form_html += u'<input type="file" name="myfile" /></td></tr>'
       form_html += u'</table>'
       return form_html
  
    def GET(self):
       form = self.dance_add_form()
       form_html = self.form_manual(form, validate=True) 
       return render.add_dance(form_html)

    def POST(self):
      
        form = self.dance_add_form()
        inp = web.input(img=[])
        photo = inp.get("img")
        if not form.validates() or photo == []:  
            form_html = self.form_manual(form, validate=True)
            return render.add_dance(form_html)
        else:  
            form.title.value = clean_str(form.d.title)           
            new_did = db.insert('dances', **form.d)
            inp = web.input(img=[])
            photo = inp.get("img")
            for pid in photo:
               db.insert('photo_img', did=new_did, pid=pid)
            x = web.input(myfile={})
            filedir = 'static/design/img' 
            if 'myfile' in x: 
               filepath=x.myfile.filename.replace('\\','/')
               filename=filepath.split('/')[-1]
               fout = open(filedir +'/'+ filename,'wb')
               fout.write(x.myfile.file.read())
               fout.close()
            raise web.seeother('/dance/%s/%d' % (form.d.title.replace(" ", "_"), new_did))
          
if __name__ == "__main__":
    app = web.application(urls, globals())
    web.httpserver.runsimple(app.wsgifunc(), ("127.0.0.1", 12345))
    #web.httpserver.runsimple(app.wsgifunc(), ("172.16.8.15", 1234))
       

