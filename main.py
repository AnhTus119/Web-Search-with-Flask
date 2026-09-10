# This is a sample Python script.
from flask import Flask, render_template, request
from auth.routes import auth_bp
from search.routes import search_bp

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

app:Flask = Flask (__name__)
app.secret_key = '123456'

app.register_blueprint(auth_bp)
app.register_blueprint(search_bp)

app.template_folder = "templates"


# @app.route("/")
# def index():
#     return render_template("Search.html",
#                            search_text = "")
#
# @app.route('/search', methods=['POST'])
# def search():
#     #Get data from Request
#     my_search_text = request.form['searchInput']
#     #Add Code
#     html_table = load_data(my_search_text)
#     return render_template('Search.html',
#                            search_text=my_search_text, table = html_table)
#
# def load_data(search_text):
#     import pandas as pd
#     #Đọc dữ liệu từ csv và lọc
#     df = pd.read_csv('gradedata.csv')
#     dfX = df
#     if search_text != "":
#         #Hoặc là fname | lname
#         dfX = df[(df["fname"] == search_text) |
#                  (df["lname"] == search_text)]
#         print(dfX)
#     html_table = dfX.to_html(classes='data',
#                              escape=False)
#     return html_table


if __name__ == '__main__':
    app.run(debug=True)