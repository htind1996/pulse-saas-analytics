import os

import mysql.connector

from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import generate_password_hash


load_dotenv()


app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


def get_database_connection():

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    return connection


@app.route("/")
def welcome():

    return render_template("welcome.html")


@app.route("/register", methods=["POST"])
def register():

    full_name = request.form["full_name"]
    email = request.form["email"]
    password = request.form["password"]

    session["full_name"] = full_name
    session["email"] = email
    session["password"] = password

    return redirect(url_for("details"))


@app.route("/details")
def details():

    if "email" not in session:

        return redirect(url_for("welcome"))

    return render_template(
        "details.html",
        full_name=session["full_name"]
    )


@app.route("/complete-registration", methods=["POST"])
def complete_registration():

    full_name = session["full_name"]

    email = session["email"]

    password = session["password"]


    company_name = request.form["company_name"]

    country = request.form["country"]

    industry = request.form["industry"]

    company_size = request.form["company_size"]

    job_role = request.form["job_role"]

    plan_type = request.form["plan_type"]


    marketing_consent = (
        request.form.get("marketing_consent") == "on"
    )


    password_hash = generate_password_hash(password)


    connection = get_database_connection()

    cursor = connection.cursor()


    query = """
        INSERT INTO users
        (
            full_name,
            email,
            password_hash,
            company_name,
            country,
            industry,
            company_size,
            job_role,
            plan_type,
            marketing_consent
        )

        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """


    values = (
        full_name,
        email,
        password_hash,
        company_name,
        country,
        industry,
        company_size,
        job_role,
        plan_type,
        marketing_consent
    )


    cursor.execute(query, values)

    connection.commit()


    cursor.close()

    connection.close()


    session.clear()


    return render_template(
        "thankyou.html",
        full_name=full_name
    )

application = app 


if __name__ == "__main__":

    app.run(debug=True)
