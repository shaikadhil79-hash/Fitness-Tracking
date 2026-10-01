from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import make_response

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)
# =====================================================
# JWT CONFIGURATION
# =====================================================

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

app.config['JWT_COOKIE_CSRF_PROTECT'] = False

jwt = JWTManager(app)

# =====================================================
# DATABASE CONNECTION
# =====================================================

conn = psycopg2.connect(
    host="localhost",
    database="fitness_db",
    user="postgres",
    password="MYDATABASE@1051",
    port="5432"
)

# =====================================================
# HOME PAGE
# =====================================================

@app.route('/')
def home():

    return render_template(
        'login.html'
    )

# =====================================================
# REGISTER USER
# =====================================================

@app.route(
    '/register',
    methods=['POST']
)
def register():

    try:

        name = request.form['name']

        email = request.form.get('email')

        phone = request.form['phone']

        password = request.form['password']

        hashed_password = (
            generate_password_hash(
                password
            )
        )

        cur = conn.cursor()

        query = """
        INSERT INTO users(
            name,
            email,
            phone,
            password
        )
        VALUES(%s,%s,%s,%s)
        """

        cur.execute(

            query,

            (
                name,
                email,
                phone,
                hashed_password
            )
        )

        conn.commit()

        cur.close()

        return """
        <script>

        alert(
        'Registration Successful'
        );

        window.location.href='/';

        </script>
        """

    except Exception as e:

        return str(e)

# =====================================================
# LOGIN USER
# =====================================================

@app.route(
    '/login',
    methods=['POST']
)
def login():

    try:

        email = request.form['email']

        password = request.form['password']

        cur = conn.cursor()

        query = """
        SELECT name,password
        FROM users
        WHERE email=%s
        """

        cur.execute(
            query,
            (email,)
        )

        user = cur.fetchone()

        cur.close()

        if user:

            stored_name = user[0]

            stored_password = user[1]

            if check_password_hash(
                stored_password,
                password
            ):

                # ============================================
                # CHECK PROFILE EXISTS
                # ============================================

                profile_cur = conn.cursor()

                profile_cur.execute(
                    """
                    SELECT *
                    FROM user_profile
                    WHERE email=%s
                    """,
                    (email,)
                )

                profile = (
                    profile_cur.fetchone()
                )

                profile_cur.close()

                # ============================================
                # CREATE JWT TOKEN
                # ============================================

                access_token = (
                    create_access_token(
                        identity=email
                    )
                )

                # ============================================
                # REDIRECT
                # ============================================

                if profile:

                    response = make_response(

                        redirect(
                            f'/dashboard/{stored_name}/{email}'
                        )
                    )

                else:

                    response = make_response(

                        redirect(
                            f'/profile/{stored_name}/{email}'
                        )
                    )

                response.set_cookie(
                    'access_token_cookie',
                    access_token
                )

                return response

        return """
        <script>

        alert(
        'Invalid Email or Password'
        );

        window.location.href='/';

        </script>
        """

    except Exception as e:

        return str(e)

# =====================================================
# PROFILE PAGE
# =====================================================

@app.route('/profile/<name>/<path:email>')
def profile_page(name,email):

    cur = conn.cursor()

    cur.execute("""
        SELECT profile_image
        FROM fitness_profile
        WHERE email=%s
    """,(email,))

    result = cur.fetchone()

    if result:
        profile_image = result[0]
    else:
        profile_image = ""

    return render_template(
        'profile.html',
        name=name,
        email=email,
        profile_image=profile_image
    )
@app.route('/upload_profile_photo', methods=['POST'])
def upload_profile_photo():

    try:

        email = request.form.get('email')

        file = request.files.get('profile_image')

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            filepath = os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )

            file.save(filepath)

            cur = conn.cursor()

            cur.execute(
                """
                UPDATE user_profile
                SET profile_image=%s
                WHERE email=%s
                """,
                (filename, email)
            )

            conn.commit()

            cur.close()

        return redirect(request.referrer)

    except Exception as e:

        return str(e)

# =====================================================
# SAVE PROFILE
# =====================================================

@app.route(
    '/save_profile',
    methods=['POST']
)
@jwt_required(
    locations=["cookies"]
)
def save_profile():

    try:

        email = request.form['email']

        height = request.form.get('height')

        weight = request.form.get('weight')

        age = request.form.get('age')

        gender = request.form['gender']

        activity_level = (
            request.form[
                'activity_level'
            ]
        )

        goal = request.form['goal']

        health_conditions = (
            request.form[
                'health_conditions'
            ]
        )

        diet_preferences = (
            request.form[
                'diet_preferences'
            ]
        )

        cur = conn.cursor()

        query = """
        INSERT INTO user_profile(

            email,
            height,
            weight,
            age,
            gender,
            activity_level,
            goal,
            health_conditions,
            diet_preferences

        )
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        cur.execute(

            query,

            (
                email,
                height,
                weight,
                age,
                gender,
                activity_level,
                goal,
                health_conditions,
                diet_preferences
            )
        )

        conn.commit()

        cur.close()

        cur = conn.cursor()

        cur.execute(
            """
            SELECT name
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cur.fetchone()

        stored_name = user[0]

        cur.close()

        return redirect(
            f'/dashboard/{stored_name}/{email}'
        )

    except Exception as e:

        return str(e)

# =====================================================
# DASHBOARD
# =====================================================

@app.route('/dashboard/<name>/<path:email>')
@jwt_required(locations=["cookies"])
def dashboard(name,email):

    try:
        cur = conn.cursor()
        

        cur.execute("""
            SELECT *
            FROM workouts
            WHERE email = %s
            ORDER BY workout_date DESC
        """, (email,))

        workouts = cur.fetchall()
        # ============================================
        # FETCH WORKOUT HISTORY
        # ============================================

        query = """
        SELECT workout_type,
               exercise_name,
               sets,
               reps,
               duration,
               calories,
               workout_date
        FROM workouts
        WHERE email=%s
        ORDER BY workout_date DESC
        """

        cur.execute(
            query,
            (email,)
        )

        workouts = cur.fetchall()

        # ============================================
        # TOTAL CALORIES
        # ============================================

        cur.execute(
            """
            SELECT COALESCE(
            SUM(calories),0)
            FROM workouts
            WHERE email=%s
            """,
            (email,)
        )

        total_calories = (
            cur.fetchone()[0]
        )

        # ============================================
        # TOTAL DURATION
        # ============================================

        cur.execute(
            """
            SELECT COALESCE(
            SUM(duration),0)
            FROM workouts
            WHERE email=%s
            """,
            (email,)
        )

        total_duration = (
            cur.fetchone()[0]
        )

        # ============================================
        # TOTAL WORKOUT COUNT
        # ============================================

        cur.execute(
            """
            SELECT COUNT(*)
            FROM workouts
            WHERE email=%s
            """,
            (email,)
        )

        workout_count = (
            cur.fetchone()[0]
        )

        # ============================================
        # CHART DATA
        # ============================================

        cur.execute(
            """
            SELECT DATE(workout_date),
                   SUM(calories)
            FROM workouts
            WHERE email=%s
            GROUP BY DATE(workout_date)
            ORDER BY DATE(workout_date)
            """,
            (email,)
        )

        weekly_data = (
            cur.fetchall()
        )

        chart_labels = [

            str(row[0])

            for row in weekly_data
        ]

        chart_values = [

            row[1]

            for row in weekly_data
        ]

        # ============================================
        # FETCH USER GOAL
        # ============================================

        cur.execute(
            """
            SELECT goal
            FROM user_profile
            WHERE email=%s
            """,
            (email,)
        )

        goal_data = (
            cur.fetchone()
        )

        goal = goal_data[0]

        # ============================================
        # AI RECOMMENDATION
        # ============================================

        if total_calories < 1000:

            recommendation = """
            Increase cardio workouts
            to improve calorie burn.
            """

        elif total_calories < 3000:

            recommendation = """
            Great consistency.
            Maintain your routine.
            """

        else:

            recommendation = """
            Excellent performance.
            Focus on recovery.
            """

        # ============================================
        # DIET PLAN
        # ============================================

        if goal == 'Lose Fat':

            diet_plan = [

                {
                    "day":"Day 1",

                    "breakfast":
                    "2 besan chilla + curd + green tea",

                    "lunch":
                    "2 phulka + moong dal + sabzi + salad",

                    "dinner":
                    "Veg soup + 1 phulka + mixed sabzi",

                    "snacks":
                    "Apple + roasted chana"
                },

                {
                    "day":"Day 2",

                    "breakfast":
                    "Egg omelette + multigrain toast",

                    "lunch":
                    "Brown rice + rajma + salad",

                    "dinner":
                    "2 phulka + lauki sabzi + dal",

                    "snacks":
                    "Papaya + green tea"
                }
            ]

        elif goal == 'Gain Muscle':

            diet_plan = [

                {
                    "day":"Day 1",

                    "breakfast":
                    "Oats + milk + banana + peanut butter",

                    "lunch":
                    "Chicken + rice + vegetables",

                    "dinner":
                    "Paneer + chapati + salad",

                    "snacks":
                    "Protein shake + almonds"
                },

                {
                    "day":"Day 2",

                    "breakfast":
                    "Eggs + toast + fruits",

                    "lunch":
                    "Fish + brown rice + vegetables",

                    "dinner":
                    "Tofu + quinoa + soup",

                    "snacks":
                    "Greek yogurt + nuts"
                }
            ]

        else:

            diet_plan = [

                {
                    "day":"Day 1",

                    "breakfast":
                    "Poha + sprouts",

                    "lunch":
                    "Dal + rice + sabzi",

                    "dinner":
                    "Soup + chapati + vegetables",

                    "snacks":
                    "Fruits + green tea"
                }
            ]

        cur.close()

        return render_template(

          'dashboard.html',

           name=name,

            email=email,

            workouts=workouts,

            total_calories=total_calories,

            total_duration=total_duration,

            workout_count=workout_count,

            recommendation=recommendation,

            chart_labels=chart_labels,

            chart_values=chart_values,

            diet_plan=diet_plan
        )
    except Exception as e:

        return render_template(
            "dashboard.html",
            name=name,
            email=email,
            workouts=workouts
)
# =====================================================
# NUTRITION PAGE
# =====================================================

@app.route('/nutrition/<path:email>', methods=['GET'])
@jwt_required(locations=["cookies"])
def nutrition_page(email):

    return render_template(
        'nutrition.html',
        email=email,
        nutrition=None
    )


@app.route('/nutrition/<path:email>', methods=['POST'])
@jwt_required(locations=["cookies"])
def generate_nutrition(email):

    goal = request.form['goal']

    if goal == "Lose Fat":

        nutrition = {
            "calories":1800,
            "protein":130,
            "carbs":150,
            "fats":50,
            "breakfast":"Oats + Eggs",
            "lunch":"Chicken + Rice + Salad",
            "dinner":"Fish + Vegetables",
            "snacks":"Fruits + Nuts"
        }

    elif goal == "Gain Muscle":

        nutrition = {
            "calories":2800,
            "protein":180,
            "carbs":320,
            "fats":80,
            "breakfast":"Oats + Banana + Peanut Butter",
            "lunch":"Chicken + Rice",
            "dinner":"Paneer + Chapati",
            "snacks":"Protein Shake"
        }

    else:

        nutrition = {
            "calories":2200,
            "protein":150,
            "carbs":250,
            "fats":70,
            "breakfast":"Poha + Sprouts",
            "lunch":"Dal + Rice",
            "dinner":"Vegetable Soup",
            "snacks":"Fruits"
        }

    return render_template(
        'nutrition.html',
        email=email,
        nutrition=nutrition
    )
    @app.route('/ai_coach/<path:email>')
    def ai_coach(email):

     return render_template(
        'ai_coach.html',
        email=email,
        question=None,
        answer=None
    )
    # =====================================================
# AI COACH
# =====================================================

@app.route('/ai_coach/<path:email>', methods=['GET', 'POST'])
def ai_coach(email):

    question = None
    answer = None

    if request.method == 'POST':

        question = request.form['question']

        answer = f"""
        Based on your question:

        {question}

        Maintain a balanced diet,
        consume enough protein,
        stay hydrated,
        and follow your workout plan consistently.
        """

    return render_template(
        'ai_coach.html',
        email=email,
        question=question,
        answer=answer
    )


# =====================================================
# COMMUNITY
# =====================================================

@app.route('/community/<path:email>')
def community(email):

    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM community_posts
        ORDER BY created_at DESC
        """
    )

    posts = cur.fetchall()

    cur.close()

    return render_template(
        'community.html',
        email=email,
        posts=posts
    )

@app.route('/create_post', methods=['POST'])
def create_post():

    email = request.form.get('email')
    content = request.form.get('content')
    
    if not content:
        return redirect(
            url_for(
                'community',
                email=email
            )
        )

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO community_posts
        (email, content)
        VALUES (%s, %s)
        """,
        (email, content)
    )

    conn.commit()

    cur.close()

    return redirect(
        url_for(
            'community',
            email=email
        )
    )
# =====================================================
# CHALLENGES
# =====================================================

@app.route('/challenges/<path:email>')
def challenges(email):

    return render_template(
        'challenges.html',
        email=email
    )

    
# =====================================================
# WORKOUT PAGE
# =====================================================

@app.route(
    '/workout/<path:email>'
)
@jwt_required(
    locations=["cookies"]
)
def workout_page(email):

    return render_template(
        'workout.html',
        email=email
    )

# =====================================================
# ADD WORKOUT
# =====================================================

@app.route(
    '/add_workout',
    methods=['POST']
)
@jwt_required(
    locations=["cookies"]
)
def add_workout():

    try:

        email = request.form['email']

        workout_types = (
            request.form.getlist(
                'workout_type[]'
            )
        )

        exercise_names = (
            request.form.getlist(
                'exercise_name[]'
            )
        )

        reps_list = (
            request.form.getlist(
                'reps[]'
            )
        )

        sets_list = (
            request.form.getlist(
                'sets[]'
            )
        )

        durations = (
            request.form.getlist(
                'duration[]'
            )
        )

        duration_types = (
            request.form.getlist(
                'duration_type[]'
            )
        )

        workout_times = (
            request.form.getlist(
                'workout_time[]'
            )
        )

        cur = conn.cursor()

        for i in range(
            len(workout_types)
        ):

            workout_type = (
                workout_types[i]
            )

            exercise_name = (
                exercise_names[i]
            )

            reps = (
                reps_list[i]
                if reps_list[i]
                else None
            )

            sets = (
                sets_list[i]
                if sets_list[i]
                else None
            )

            duration = int(
                durations[i]
            )

            duration_type = (
                duration_types[i]
            )

            workout_time = (
                workout_times[i]
            )

            # ============================================
            # HOURS TO MINUTES
            # ============================================

            if duration_type == 'hours':

                duration = (
                    duration * 60
                )
                

            # ============================================
            # CALORIES CALCULATION
            # ============================================

            if workout_type == 'Running':

                calories = duration * 10

            elif workout_type == 'Cycling':

                calories = duration * 8

            elif workout_type == 'Gym':

                calories = duration * 7

            elif workout_type == 'Yoga':

                calories = duration * 4

            elif workout_type == 'Swimming':

                calories = duration * 9

            else:

                calories = duration * 5

            query = """
            INSERT INTO workouts(

                email,
                workout_type,
                exercise_name,
                reps,
                sets,
                duration,
                calories,
                workout_date

            )
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
            """

            cur.execute(

                query,

                (
                    email,
                    workout_type,
                    exercise_name,
                    reps,
                    sets,
                    duration,
                    calories,
                    workout_time
                )
            )

        conn.commit()

        cur.close()

        # ============================================
        # FETCH USER NAME
        # ============================================

        cur = conn.cursor()

        cur.execute(
            """
            SELECT name
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cur.fetchone()

        stored_name = user[0]

        cur.close()

        return redirect(
            f'/dashboard/{stored_name}/{email}'
        )

    except Exception as e:

        return str(e)

# =====================================================
# LOGOUT
# =====================================================

@app.route('/logout')
def logout():

    response = redirect('/')

    response.delete_cookie(
        'access_token_cookie'
    )

    return response

# =====================================================
# RUN SERVER
# =====================================================

if __name__ == '__main__':

    app.run(debug=True)