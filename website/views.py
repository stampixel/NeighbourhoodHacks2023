import os
import uuid
from datetime import datetime

import boto3
import pymongo
from flask import Blueprint, render_template, redirect, request, flash, url_for, abort, session
import random
import string
import requests
from . import app, db
from dotenv import load_dotenv
import os
import googlemaps

users = db.Users
posts = db.Posts

views = Blueprint('views', __name__)
gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))


# Index page
@views.route('/')
def index():
    if 'username' in session:
        user = users.find({'username': session['username']})
        return redirect(url_for('views.editor'))
    else:
        return render_template('homepage.html', user=False)


# NOTE EDITOR
def upload_file_to_s3(file, bucket_name, acl="public-read"):
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=app.config['S3_KEY'],
            aws_secret_access_key=app.config['S3_SECRET']
        )
        file.seek(0)
        s3.upload_fileobj(
            file,
            bucket_name,
            session['username'] + "/" + file.filename,
            # file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("Something Happened: ", e)


def get_posts():
    return list(users.find({}).sort('timestamp', pymongo.DESCENDING))


def get_user_posts():
    return list(posts.find({'username': session['username']}).sort('timestamp', pymongo.DESCENDING))


def get_coords(address: str):
    geocode_result = gmaps.geocode(address)
    return [geocode_result[0]['geometry']['location']['lat'], geocode_result[0]['geometry']['location']['lng']]


@views.route('/editor', methods=['GET', 'POST'])
def editor():
    print('Request for upload received')
    if "username" not in session:
        return redirect(url_for("views.index"))
    if request.method == "POST":
        try:
            if request.form['save-content'] == "Save Content":
                try:
                    image = request.files['pfp']
                    if image.filename != "":
                        image.filename = 'pfp'
                        upload_file_to_s3(image, app.config["S3_BUCKET"])
                        file_location = 'http://' + os.getenv('S3_BUCKET_NAME') + '.s3.amazonaws.com/' + session[
                            "username"] + "/pfp"
                        users.find_one_and_update({'username': session['username']},
                                                  {'$set': {'profile_picture': file_location}})
                except Exception as e:
                    flash("An error has occurred, please try again later.", "error")

                try:
                    image = request.files['banner']
                    if image.filename != "":
                        image.filename = 'banner'
                        upload_file_to_s3(image, app.config["S3_BUCKET"])
                        file_location = 'http://' + os.getenv('S3_BUCKET_NAME') + '.s3.amazonaws.com/' + session[
                            "username"] + "/banner"
                        users.find_one_and_update({'username': session['username']},
                                                  {'$set': {'banner': file_location}})
                except Exception as e:
                    flash("An error has occurred, please try again later.", "error")

                try:
                    if request.form.get('name') != "":
                        username = request.form['name']
                        users.find_one_and_update({'username': session['username']},
                                                  {'$set': {'business_name': username}})
                        print("asdsd")
                except:
                    pass
        except:
            pass

        try:
            if request.form['save-address'] == "Save Address":
                address = request.form['address']
                users.find_one_and_update({'username': session['username']},
                                          {'$set': {'address': address}})
        except:
            pass

        try:
            if request.form['save-link'] == "Add Link":
                url = request.form['url']
                title = request.form['title']
                users.find_one_and_update({'username': session['username']},
                                          {'$push': {'link_tree': [url, title]}})
        except:
            pass
        # try:
        #     if request.form['save-link'] == "Save Link":
        #         link = request.form['link']
        #         users.find_one_and_update({'username': session['username']},
        #                                   {'$set': {'link_url': link}})
        # except:
        #     pass

        try:
            if request.form['post-image'] == "Post Image":
                print("sdfasdf")
                image = request.files['post']
                image.seek(0)

                # Generating image ID
                image_id = uuid.uuid4().hex
                image.filename = image_id

                upload_file_to_s3(image, app.config["S3_BUCKET"])
                file_location = 'http://' + os.getenv('S3_BUCKET_NAME') + '.s3.amazonaws.com/' + session[
                    "username"] + "/" + image.filename

                description = request.form.get("description")

                post_input = {'_id': image_id,
                              'timestamp': datetime.utcnow(),
                              'username': session['username'],
                              'image': file_location,
                              'description': description,
                              'likes': 0,
                              'liked_users': [],
                              'comments': []
                              }
                posts.insert_one(post_input)
                users.find_one_and_update({'username': session['username']}, {'$push': {'posts': post_input}})
        except:
            pass

    user = users.find_one({'username': session['username']})
    post_contents = get_user_posts()
    print(post_contents)
    return render_template("editor.html", user=user, posts=post_contents)


@views.route('/map', methods=['GET', 'POST'])
def map():
    # Get shops data from OpenStreetMap
    map_posts = get_posts()

    # Initialize variables
    markers = ''
    for node in map_posts:

        marker_id = "post_" + str(node["_id"])

        # Check if shops have name and website in OSM
        print(node['banner'])
        try:
            image = node["banner"]
        except:
            image = 'null'

        try:
            name = node["business_name"]
        except:
            name = 'null'

        try:
            print(node['address'])
            coords = get_coords(node['address'])

            lat = coords[0] + (random.random() - .5) * .001
            lon = coords[1] + (random.random() - .5) * .001
        except:
            continue

            # print("no lat")
            # lat = 47.7606092 + (random.random() - .5) * .00001
            # lon = -122.188031 + (random.random() - .5) * .00001

        # Create the marker and its pop-up
        markers += f"var {marker_id} = L.marker([{lat}, {lon}]);\
                    {marker_id}.addTo(map).bindPopup(\'<a class=\"mapPost\" href=\"/{node['username']}\"><img src=\"{image}\"><div class=\"mapPostCaption\">{name}</div></a>\'); "

    # Render the page with the map
    if "username" in session:
        return render_template('map.html', markers=markers, user=True)
    return render_template('map.html', markers=markers)


@views.route('/about', methods=['GET', 'POST'])
def about():
    if 'username' not in session:
        return render_template("about.html", user=False)
    return url_for("views.editor")


@views.route('/delete/<int:index>')
def delete_link(index):
    user = users.find_one({'username': session['username']})
    links = user['link_tree']
    links.pop(index - 1)

    users.find_one_and_update({'username': session['username']},
                              {'$set': {'link_tree': links}})
    return redirect(url_for('views.editor'))


@views.route('/delete/post/<id>')
def delete_post(id):
    if "username" in session:
        posts.delete_one({'_id': id})
        return redirect(url_for('views.editor'))
    return redirect(url_for('views.index'))


@views.route('/<username>')
def business(username):
    user = users.find_one({"username": username})

    return render_template("business.html", user=user)
