import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bimcom_test"
)
myCursor = db.cursor()


def get_lga_list():
    myCursor.execute("SELECT lga_id, lga_name FROM lga")
    return myCursor.fetchall()


def get_lga_name_by_id(lga_id):
    query = "SELECT lga_name FROM lga WHERE lga_id = %s;"
    myCursor.execute(query,(lga_id,))
    lga_name = myCursor.fetchone()
    return lga_name[0] if lga_name else None


def get_polling_unit_unique_ids(lga_id):
    query = "SELECT uniqueid FROM polling_unit WHERE lga_id = %s;"
    myCursor.execute(query,(lga_id,))
    return [row[0] for row in myCursor.fetchall()]


def get_party_scores(polling_unit_unique_ids):
    party_scores = {}

    for id in polling_unit_unique_ids:
        query = "SELECT party_abbreviation, party_score FROM announced_pu_results WHERE polling_unit_uniqueid = %s"
        myCursor.execute(query,(id,))
        lga_result = myCursor.fetchall()

        for abbreviation,score in lga_result:
            if abbreviation in party_scores:
                party_scores[abbreviation] += score
            else:
                party_scores[abbreviation] = score

    return party_scores


def get_polling_units():
    myCursor.execute("SELECT uniqueid, polling_unit_name FROM polling_unit")
    return myCursor.fetchall()


def find_scores(polling_uuid):
    announced_pu_results_query = ("SELECT party_abbreviation, party_score FROM announced_pu_results WHERE "
                                  "polling_unit_uniqueid = %s")
    try:
        myCursor.execute(announced_pu_results_query,(polling_uuid,))
        announced_pu_data = myCursor.fetchall()
        announced_pu_scores = {abbreviation:score for abbreviation,score in announced_pu_data}
        return announced_pu_scores
    except mysql.connector.Error as e:
        print("Error executing query: ",e)
        return None


def get_polling_unit_name_by_id(polling_uuid):
    polling_units = get_polling_units()
    for id,name in polling_units:
        if id == polling_uuid:
            return name
    return None
