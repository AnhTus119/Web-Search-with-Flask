from flask import Blueprint, request, render_template, session, redirect, url_for
import pandas as pd

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET', 'POST'])
def search():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    search_text = ''
    html_table = ''

    if request.method == 'POST':
        search_text = request.form['searchInput']
        html_table = load_data(search_text)

    return render_template(
        'Search.html',
        search_text=search_text,
        table=html_table
    )

def load_data(search_text):
    df = pd.read_csv('gradedata.csv')

    if search_text != '':
        df = df[
            df['address']
            .fillna('')
            .astype(str)
            .str.contains(search_text, case=False, na=False, regex=False)
            |
            df['fname']
            .fillna('')
            .astype(str)
            .str.contains(search_text, case=False, na=False, regex=False)
        ]

    return df.to_html(classes='data', escape=False)