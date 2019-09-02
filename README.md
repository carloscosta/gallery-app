
# Image gallery

A gallery web app that can be used to collect wedding photos where you and your
friends will be able to upload photos in an unified gallery of your photos with 
all friend's photos. You (the admin) will be able to approve the photos before
be visible to everyone. Visitors are able to like photos, sorting the dashboard
of photos by total of likes or by date taken.

The app follows the Model-View-Controller pattern. Backend and Frontend is
coded to follow the separation beetween views and models, as the design pattern
indicates.

## Backend

The Gallery app uses [Python CherryPy](https://cherrypy.org/) as the controller,
[Jinja2](https://palletsprojects.com/p/jinja/) for the templating views, 
[Mongodb](https://cloud.mongodb.com/v2/) through the excelent 
[mongoengine](http://mongoengine.org/), which provide ORM features. Finally, the
images are saved into an [AWS S3](https://aws.amazon.com/s3/) bucket using 
the [Boto3](https://aws.amazon.com/sdk-for-python/) AWS SDK.

## Frontend
 
Web interface was designed using the excellent [Twitter Bootstrap](https://getbootstrap.com/) 
plus [Open Iconic](https://useiconic.com/open/) on button's ico, and  
[Lightbox for Bootstrap](http://ashleydw.github.io/lightbox/) which utilizes Bootstrap's modal 
plugin to implement a lightbox gallery. 

## Steps to run the app

Clone the repository:

    $ git clone https://github.com/carloscosta/gallery-app
    $ cd gallery-app/

Always using Python Enviroments on your projects, create it

    $ python3 -m venv .gallery
    $ source .gallery/bin/activate

fulfill the requirements installing all the packages needed:

    $ pip install -r requirements.txt
 
CherryPy comes with a set of simple tutorials that can be executed once you 
have deployed the package in the enviromment. To check if everything is working fine:

    $ python -m cherrypy.tutorial.tut00_helloworld

If the `helloworld` app works well, its time to fill the `run.conf` file with the strings used
in the connections to the Mongodb and AWS S3 services. Edit the file with your editor, you should 
be able to provide the following information:

    export admin_password=""
    export bucket_name=""
    export bucket_url=""
    export aws_access_key_id=""
    export aws_secret_access_key=""
    export mongo_db_str=""

Finally, to run the app:

    $ bash run.sh

## Diving into the source code

A overview of the directories and the source code organization is presented
below:

    dev.conf
    Gallery/
        assets/
        base.html
        index.html
        __init__.py
        login.html
        upload.html
    prod.conf
    README.md
    requirements.txt
    run.conf
    run.sh

The `run.sh` is the entry point to run the app, should be configure using the
`run.conf` file as mentioned early. Inside the `Gallery/` directory, all the
Jinja2 templates are organized. The `base.html` template is the root.

The `__init__.py` file is where the magic happens. Finally, the `Gallery/assets/`
contains the static content (CSS, JS and vendor stuffs) which is served
statically.

