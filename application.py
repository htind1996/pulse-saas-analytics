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


# --------------------------------------------------
# ANALYTICS SESSION
# --------------------------------------------------

def get_analytics_session_id():

    if "analytics_session_id" not in session:

        session["analytics_session_id"] = os.urandom(16).hex()

    return session["analytics_session_id"]


# --------------------------------------------------
# EVENT TRACKING
# --------------------------------------------------

def track_event(event_name, user_id=None):

    analytics_session_id = get_analytics_session_id()

    connection = get_database_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO events
        (
            user_id,
            session_id,
            event_name
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
    """

    values = (
        user_id,
        analytics_session_id,
        event_name
    )

    cursor.execute(
        query,
        values
    )

    connection.commit()

    cursor.close()

    connection.close()


# --------------------------------------------------
# WELCOME PAGE
# --------------------------------------------------

@app.route("/")
def welcome():

    get_analytics_session_id()

    track_event("page_view")

    return render_template("welcome.html")


# --------------------------------------------------
# REGISTRATION START
# --------------------------------------------------

@app.route("/register", methods=["POST"])
def register():

    full_name = request.form["full_name"]
    email = request.form["email"]
    password = request.form["password"]

    session["full_name"] = full_name
    session["email"] = email
    session["password"] = password

    track_event("registration_started")

    return redirect(url_for("details"))


# --------------------------------------------------
# DETAILS PAGE
# --------------------------------------------------

@app.route("/details")
def details():

    if "email" not in session:

        return redirect(url_for("welcome"))

    track_event("details_viewed")

    return render_template(
        "details.html",
        full_name=session["full_name"]
    )


# --------------------------------------------------
# COMPLETE REGISTRATION
# --------------------------------------------------

@app.route("/complete-registration", methods=["POST"])
def complete_registration():

    full_name = session["full_name"]
    email = session["email"]
    password = session["password"]

    analytics_session_id = get_analytics_session_id()

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

    try:

        # CREATE USER

        user_query = """
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

        user_values = (
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

        cursor.execute(
            user_query,
            user_values
        )


        # GET NEW USER ID

        user_id = cursor.lastrowid


        # LINK ANONYMOUS SESSION EVENTS TO USER

        link_events_query = """
            UPDATE events

            SET user_id = %s

            WHERE session_id = %s

            AND user_id IS NULL
        """

        cursor.execute(
            link_events_query,
            (
                user_id,
                analytics_session_id
            )
        )


        # TRACK USER REGISTERED EVENT

        registered_event_query = """
            INSERT INTO events
            (
                user_id,
                session_id,
                event_name
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
        """

        cursor.execute(
            registered_event_query,
            (
                user_id,
                analytics_session_id,
                "user_registered"
            )
        )


        # COMMIT EVERYTHING TOGETHER

        connection.commit()


    except Exception:

        connection.rollback()

        raise


    finally:

        cursor.close()

        connection.close()


    # REMOVE REGISTRATION DATA
    # PRESERVE ANALYTICS SESSION

    session.pop("full_name", None)

    session.pop("email", None)

    session.pop("password", None)


    return render_template(
        "thankyou.html",
        full_name=full_name
    )


# --------------------------------------------------
# ANALYTICS DASHBOARD
# --------------------------------------------------

@app.route("/admin/analytics")
def analytics():

    connection = get_database_connection()

    cursor = connection.cursor(dictionary=True)


    # KPI METRICS

    cursor.execute("""
        SELECT
            COUNT(*) AS total_users,

            SUM(
                CASE
                    WHEN plan_type = 'Free'
                    THEN 1
                    ELSE 0
                END
            ) AS free_users,

            SUM(
                CASE
                    WHEN plan_type != 'Free'
                    THEN 1
                    ELSE 0
                END
            ) AS paid_users,

            SUM(
                CASE
                    WHEN marketing_consent = 1
                    THEN 1
                    ELSE 0
                END
            ) AS marketing_users

        FROM users
    """)

    metrics = cursor.fetchone()


    # USERS BY PLAN

    cursor.execute("""
        SELECT
            plan_type,
            COUNT(*) AS user_count

        FROM users

        GROUP BY plan_type

        ORDER BY user_count DESC
    """)

    plan_distribution = cursor.fetchall()


    # USERS BY COUNTRY

    cursor.execute("""
        SELECT
            country,
            COUNT(*) AS user_count

        FROM users

        GROUP BY country

        ORDER BY user_count DESC
    """)

    country_distribution = cursor.fetchall()


    # EVENT METRICS

    cursor.execute("""
        SELECT
            COUNT(*) AS total_events,

            COUNT(
                DISTINCT CASE
                    WHEN event_timestamp >= NOW() - INTERVAL 1 DAY
                    THEN session_id
                END
            ) AS daily_active_users

        FROM events
    """)

    event_metrics = cursor.fetchone()


    # EVENT DISTRIBUTION

    cursor.execute("""
        SELECT
            event_name,
            COUNT(*) AS event_count

        FROM events

        GROUP BY event_name

        ORDER BY event_count DESC
    """)

    event_distribution = cursor.fetchall()

    # REGISTRATION FUNNEL

    cursor.execute("""
    SELECT
        COUNT(
            DISTINCT CASE
                WHEN event_name = 'page_view'
                THEN session_id
            END
        ) AS page_views,

        COUNT(
            DISTINCT CASE
                WHEN event_name = 'registration_started'
                THEN session_id
            END
        ) AS registrations_started,

        COUNT(
            DISTINCT CASE
                WHEN event_name = 'details_viewed'
                THEN session_id
            END
        ) AS details_viewed,

        COUNT(
            DISTINCT CASE
                WHEN event_name = 'user_registered'
                THEN session_id
            END
        ) AS registrations_completed

    FROM events

    WHERE session_id IS NOT NULL
""")

    funnel_metrics = cursor.fetchone()


    cursor.close()

    connection.close()


    return render_template(
    "analytics.html",
    metrics=metrics,
    plan_distribution=plan_distribution,
    country_distribution=country_distribution,
    event_metrics=event_metrics,
    event_distribution=event_distribution
    )


application = app


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )