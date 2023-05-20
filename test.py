# @app.route("/login", methods=["POST", "GET"])
# def login():
#     print('Request for login received')
#     if "username" in session:
#         return redirect(url_for("home"))
#
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")
#
#         user_found = users.find_one({"username": username})
#         if user_found:
#             user_val = user_found['username']
#             passwordcheck = user_found['password']
#
#             if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
#                 session["username"] = user_val
#                 return redirect(url_for('home'))
#             else:
#                 if "username" in session:
#                     return redirect(url_for("home"))
#                 return render_template('login.html')
#         else:
#             return render_template('login.html')
#     return render_template('login.html')