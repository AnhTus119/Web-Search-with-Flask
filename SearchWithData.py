from flask import Flask, request, render_template
app: Flask = Flask(__name__, static_url_path='/static')
#Mặc định gọi form search
@app.route('/')
def index():
    return render_template(
        'SearchWithCSSData.html', search_text="")

#Đối với phương thức Search
@app.route('/searchData', methods=['POST'])
def searchData():
    #Get data from Request
    search_text = request.form['searchInput']
    html_table = load_data(search_text)
    print(html_table)
    return render_template('SearchWithCSSData.html',
                           search_text=search_text,
                           table=html_table
                           )
#Load dữ liệu và lọc ra bản ghi phù hợp
def load_data(search_text):
    import pandas as pd
    df = pd.read_csv('gradedata.csv')
    dfX = df
    if search_text != "":
        dfX = df[(df["fname"] == search_text) |
                 (df["lname"] == search_text)]
        print(dfX)
    html_table = dfX.to_html(classes='data',
                             escape=False)
    return html_table


    # Đối với phương thức Search
@app.route('/search', methods=['POST'])
def search():
    # Get data from Request
    search_text = request.form['searchInput']
    return render_template('SearchWithCSSData.html',
                           search_text=search_text)
if __name__ == '__main__':
    app.run()