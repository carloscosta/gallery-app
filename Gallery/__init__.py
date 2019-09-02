# coding=UTF-8
# -*- coding: UTF-8 -*-

import os
import re
import boto3
import datetime
import cherrypy
import mongoengine
from botocore.exceptions import ClientError
from cherrypy.lib.static import serve_file
from jinja2 import Template, Environment, FileSystemLoader


# Access strings
admin_password = os.environ.get('admin_password')
bucket_name = os.environ.get('bucket_name')
bucket_url = os.environ.get('bucket_url')
aws_access_key_id = os.environ.get('aws_access_key_id')
aws_secret_access_key = os.environ.get('aws_secret_access_key')
mongo_db_str = os.environ.get('mongo_db_str')

# The class level variables
local_dir = os.path.dirname(__file__)
abs_dir = os.path.join(os.getcwd(), local_dir)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Env for the rendering of templates
env = Environment(loader=FileSystemLoader(current_dir), trim_blocks=True)

# mongo connection
mongoengine.connect(host=mongo_db_str)


class Image(mongoengine.Document):
    filename = mongoengine.StringField(required=True)
    title = mongoengine.StringField(required=True)
    link = mongoengine.StringField(required=True)
    status = mongoengine.StringField(default="draft")
    votes = mongoengine.IntField(default=0)
    creation = mongoengine.DateTimeField(default=datetime.datetime.utcnow)


class Root(object):
    @cherrypy.expose
    def index(self, page=1, sort_by='date'):
        cherrypy.session.load()
        items_per_page = 8 
        start_index = (int(page) - 1) * items_per_page
        end_index = int(page) * items_per_page

        dataset = None
        if sort_by == 'date':
            dataset = Image.objects[start_index:end_index].order_by('-creation')
        elif sort_by == 'votes':
            dataset = Image.objects[start_index:end_index].order_by('-votes')

        doc_total = Image.objects.count()
        total_pages = (doc_total // items_per_page) + 1
        template = env.get_template('index.html')
        cherrypy.log("index page {0} {1} {2}, {3}".format(page, doc_total, total_pages, dataset))

        if 'count' in cherrypy.session:
            cherrypy.session['count'] += 1
            return template.render(session=True, dataset=dataset, page=int(page), total=total_pages)
        return template.render(session=False, dataset=dataset, page=int(page), total=total_pages)

    def auth(self, login, password):
        if all((login, password)):
            if login.upper() == 'ADMIN' and password == admin_password:
                if 'count' not in cherrypy.session:
                    cherrypy.session['count'] = 0
                cherrypy.session['count'] += 1
                return True
        return False 

    @cherrypy.expose
    def star(self, img_id=None):
        cherrypy.session.load()
        cherrypy.log("star page {0}".format(img_id))

        if 'count' in cherrypy.session:
            cherrypy.session['count'] += 1

        if img_id:
            img = Image.objects.get(id=img_id)
            img.votes += 1
            img.save()
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def default(self, param=None):
        cherrypy.session.load()
        cherrypy.log("default page {0}".format(param))

        if 'count' in cherrypy.session:
            cherrypy.session['count'] += 1
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def remove(self, img_id=None):
        cherrypy.session.load()
        cherrypy.log("remove page {0}".format(img_id))

        if 'count' in cherrypy.session:
            cherrypy.session['count'] += 1

        if img_id:
            img = Image.objects.get(id=img_id)
            img.delete()
        raise cherrypy.HTTPRedirect("/")


    @cherrypy.expose
    def save(self, img_id=None):
        cherrypy.session.load()
        cherrypy.log("save page {0}".format(img_id))

        if 'count' in cherrypy.session:
            cherrypy.session['count'] += 1

        if img_id:
            img = Image.objects.get(id=img_id)
            img.status = 'save'
            img.save()
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def login(self, login=None, password=None, logout=False):
        cherrypy.log("login page {0}, {1}, {2}".format(login, password, logout))
        
        if logout:
            cherrypy.session['count'] = None
            cherrypy.lib.sessions.expire()
            raise cherrypy.HTTPRedirect("/")
        
        if self.auth(login, password):
            raise cherrypy.HTTPRedirect("/")

        template = env.get_template('login.html')
        return template.render()

    def s3_upload(self, file_path, file_name):
        client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)

        with open(file_path, 'rb') as data:
            try:
                response = client.upload_fileobj(data, bucket_name, file_name,
                        ExtraArgs={ "ACL": 'public-read' })
            except ClientError as e:
                cherrypy.log(e)
                return False
        return True

    @cherrypy.expose
    def upload(self, File1=None, Title1=None):
        cherrypy.session.load()
        cherrypy.log("upload page {0}, {1}".format(File1, Title1))
        session_opened = False
        if 'count' in cherrypy.session:
            cherrypy.session['count'] += 1
            session_opened = True

        if not all((File1, Title1)):
            template = env.get_template('upload.html')
            return template.render(session=session_opened)

        upload_path = os.path.dirname(__file__)
        upload_filename = re.sub('[^0-9a-zA-Z]+', '_', Title1) + ".jpg"
        upload_file = os.path.normpath(os.path.join(upload_path, upload_filename))
        upload_size = 0

        with open(upload_file, 'wb') as out:
            while True:
                data = File1.file.read(8192)
                if not data:
                    break
                out.write(data)
                upload_size += len(data)

        if self.s3_upload(upload_file, upload_filename):
            cherrypy.log('S3 upload worked {0}'.format(upload_filename))
            img = Image(filename=upload_filename, 
                    title=Title1, link=bucket_url+upload_filename)
            img.save()
        else:
            cherrypy.log('S3 upload failed {0}'.format(upload_filename))
        os.remove(upload_file)
        raise cherrypy.HTTPRedirect("/")
