from flask import Blueprint, render_template, redirect, request, flash, url_for, abort
from flask_login import login_required, current_user
import random
import string
import requests

views = Blueprint('views', __name__)

# Index page
@views.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('views.main'))
    else:
        return render_template('home.html', user=current_user)



