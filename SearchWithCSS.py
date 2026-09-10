from flask import Flask, request, render_template

app: Flask = Flask(__name__, static_url_path='/static')
#Mặc định gọi form search
@app.route('/')
def index():
    return render_template(
        'SearchWithCSS.html', search_text="")

#Đối với phương thức Search
@app.route('/search', methods=['POST'])
def search():
    #Get data from Request
    search_text = request.form['searchInput']
    return render_template('SearchWithCSS.html',
                           search_text=search_text)

if __name__ == '__main__':
    app.run()