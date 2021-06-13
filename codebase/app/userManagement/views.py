from flask import Blueprint, render_template, url_for, request, flash, redirect

# Create Blueprint
login_view = Blueprint('login_view',
                            __name__,
                            static_folder='static',
                            template_folder='templates')

@login_view.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_form = request.form
        login_email = login_form['loginEmail']
        login_pwd = login_form['loginPassword']
        login_remember = login_form['loginRemember']

        # new_discipline = Discipline(
        #     student_offender=discipline_student,
        #     discipline_grantor=discipline_teacher,
        #     reason=discipline_reason,
        #     punishment=discipline_punishment,
        #     suspension_from=suspension_from,
        #     suspension_to=suspension_to,
        #     expulsion_date=expulsion_date
        # )

        # try:
        #     # Try adding message object to database.
        #     db.session.add(new_discipline)
        #     db.session.commit()

        #     flash(
        #         f"Your Discipline entry was Successfully Recorded.")
        #     return redirect(url_for('discipline_view.all'))
        # except Exception as e:
        #     # Log this SERIOUS issue > Report to Developer
        #     error_message = e
        #     print(error_message)
        #     flash(
        #         "An Error Occurred. Please Try Again. Contact the Developer if issue persists.")
        #     return redirect(url_for('discipline_view.all'))


    return render_template("userManagement/login.html")


@login_view.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        register_form = request.form
        register_fname = register_form['registerFirst']
        register_lname = register_form['registerLast']
        register_email = register_form['registerEmail']
        register_pwd = register_form['registerPassword']
        register_confirmPwd = register_form['registerConfirmPassword']
        register_updates = register_form['registerUpdates']


    return render_template("userManagement/register.html")
