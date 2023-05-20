@app.route("/signup", methods=['POST', 'GET'])
def signup():
    print('Request for signup received')
    if "username" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form.get("username")

        password = request.form.get("password")

        user_found = users.find_one({"username": username})
        if user_found:
            return render_template('error.html', message='Username already exists.')
        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_input = {'username': username, 'password': hashed, 'profile_picture': '', 'bio': '', 'posts': []}
            users.insert_one(user_input)

            user_data = users.find_one({"username": username})
            new_username = user_data['username']

            return redirect(url_for("about"))
    return render_template('signup.html')