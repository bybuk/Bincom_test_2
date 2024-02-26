from flask import Flask,redirect,render_template,request,url_for
import mysql.connector

from config import DB_HOST, DB_USER, DB_NAME, DB_PASSWORD
from controller import get_lga_list,get_polling_unit_unique_ids,get_party_scores,get_lga_name_by_id,get_polling_units, \
    get_polling_unit_name_by_id,find_scores

app = Flask(__name__)

db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

myCursor = db.cursor()


@app.route('/')
def index():
    lga_list = get_lga_list()
    return render_template('lga_listing.html',lga_list=lga_list)


@app.route('/results', methods=['POST'])
def display_results():
    lga_id = int(request.form['lga_id'])
    lga_name = get_lga_name_by_id(lga_id)
    polling_unit_unique_ids = get_polling_unit_unique_ids(lga_id)
    party_scores = get_party_scores(polling_unit_unique_ids)
    return render_template('lga_results.html',lga_name=lga_name,party_scores=party_scores)


@app.route('/pu_list')
def pu_list():
    polling_units = get_polling_units()
    return render_template('pu_listing.html',polling_units=polling_units)


@app.route('/display_results',methods=['POST'])
def display_pu_results():
    polling_uuid = int(request.form['polling_unit'])
    polling_unit_name = get_polling_unit_name_by_id(polling_uuid)
    announced_pu_results_data = find_scores(polling_uuid)
    return render_template('pu_results.html',polling_unit_name=polling_unit_name,results=announced_pu_results_data)


@app.route('/new_polling_unit', methods=['GET','POST'])
def create_polling_unit():
    if request.method == 'POST':
        n_polling_unit_id = request.form['n_polling_unit_id']
        n_ward_id = request.form['n_ward_id']
        n_lga_id = request.form['n_lga_id']
        n_uniquewardid = request.form['n_uniquewardid']
        n_polling_unit_number = request.form['n_polling_unit_number']
        n_polling_unit_name = request.form['n_polling_unit_name']
        n_polling_unit_description = request.form['n_polling_unit_description']
        n_lat = request.form['n_lat']
        n_long = request.form['n_long']
        n_entered_by_user = request.form['n_entered_by_user']
        n_date_entered = request.form['n_date_entered']
        n_user_ip_address = request.form['n_user_ip_address']

        try:
            query = f"INSERT INTO polling_unit (polling_unit_id, ward_id, lga_id, uniquewardid, polling_unit_number, polling_unit_name, polling_unit_description, lat, long, entered_by_user, date_entered, user_ip_address) VALUES ({n_polling_unit_id}, {n_ward_id}, {n_lga_id}, {n_uniquewardid}, {n_polling_unit_number}, {n_polling_unit_name}, {n_polling_unit_description}, {n_lat}, {n_long}, {n_entered_by_user}, {n_date_entered}, {n_user_ip_address})"

            myCursor.execute(query)
            db.commit()

            myCursor.execute("SELECT uniqueid FROM polling_unit ORDER BY uniqueid DESC LIMIT 1")
            puuid = myCursor.fetchone()[0]
            return redirect(url_for('upload_results',polling_unit_id=puuid))

        except Exception as e:
            db.rollback()
            # return f"Error: {e}"

    return render_template('new_polling_unit.html')


@app.route('/upload_results/<int:polling_unit_id>', methods=['GET','POST'])
def upload_results(polling_unit_id):
    # Fetch party names
    myCursor.execute("SELECT partyname FROM party")
    party_names = [result[0] for result in myCursor.fetchall()]

    # Process party names to get abbreviations
    party_abbreviations = [name[:4] for name in party_names]

    # Initialize party_scores dictionary
    party_scores = {}

    # Loop through party abbreviations
    for party_abbr in party_abbreviations:
        score = int(request.form.get(f'score_{party_abbr}'))
        party_scores[party_abbr] = score

    # Prompt user for additional information
    pu_results_entered_by_user = request.form.get('entered_by_user','NULL')
    pu_results_date_entered = request.form.get('date_entered','NULL')
    pu_results_user_ip_address = request.form.get('user_ip_address','NULL')

    try:
        # Generate and Execute INSERT Queries
        for party_abbr,score in party_scores.items():
            insert_query = f"INSERT INTO announced_pu_results (polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user, date_entered, user_ip_address) VALUES ({polling_unit_id}, '{party_abbr}', {score}, '{pu_results_entered_by_user}', '{pu_results_date_entered}', '{pu_results_user_ip_address}')"

            myCursor.execute(insert_query)
            db.commit()

        return "Results entered successfully!"
    except Exception as e:
        db.rollback()
        return f"Error: {e}"


myCursor.close()
db.close()
if __name__ == '__main__':
    app.run(debug=True)
