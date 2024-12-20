from flask import Flask, render_template, url_for, redirect, request, session

import database

app = Flask(__name__)
app.secret_key = 'tsb_ssk'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            query = database.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password), query=True)

            session['username'] = username
            session['role'] = query[0][2]

            if session['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))

        except:
            return render_template('login.html', error_message = 'Invalid username or password.')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            database.execute('INSERT INTO users VALUES (?, ?, ?)', (username, password, 'student'))
            return redirect(url_for('login'))
        except:
            return render_template('signup.html', error_message = 'An account with that username already exists.')

    return render_template('signup.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect((url_for('login')))

    user_error_message = ''
    event_error_message = ''

    if request.method == 'POST':
        update_role_button = request.form.get('update_role')
        delete_user_button = request.form.get('delete_user')
        create_booking_button = request.form.get('create_booking')
        delete_event_button = request.form.get('delete_event')

        if update_role_button is not None:
            username = update_role_button # retrieve from value
            if username == session['username']:
                user_error_message = 'You cannot edit yourself.'
            else:
                role = request.form['user_role_' + username]
                database.execute('UPDATE users SET role=? WHERE username=?', (role, username))

        elif delete_user_button is not None:
            username = delete_user_button # retrieve from value
            if delete_user_button == session['username']:
                user_error_message = 'You cannot edit yourself.'
            else:
                database.execute('DELETE FROM users WHERE username=?', (username,))

        elif create_booking_button is not None:
            event_name = request.form['name']
            description = request.form['description']
            date = request.form['date']
            start_time = request.form['start_time']
            number_slots = request.form['number_slots']
            slot_duration = request.form['slot_duration']

            try:
                database.execute('INSERT INTO bookable_events VALUES(?, ?, ?, ?, ?, ?)', (event_name, description, date, start_time, number_slots, slot_duration))
            except:
                event_error_message = 'A bookable event with that name already exists.'

        elif delete_event_button is not None:
            event = delete_event_button
            database.execute('DELETE FROM bookable_events WHERE name=?', (event,))

    users = database.execute('SELECT * FROM users', query=True)
    bookable_events = database.execute('SELECT * FROM bookable_events', query=True)

    student_bookings = {}
    for event in bookable_events:
        student_bookings[event[0]] = database.execute('SELECT * FROM bookings WHERE event_name=?', (event[0],), query=True)

    return render_template('admin_dashboard.html',
                           users=users,
                           bookable_events=bookable_events,
                           student_bookings=student_bookings,
                           user_error_message=user_error_message,
                           event_error_message=event_error_message)

@app.route('/student', methods=['GET', 'POST'])
def student_dashboard():
    if session.get('role') != 'student':
        return redirect((url_for('login')))

    error_message = ''

    username = session.get('username')

    bookable_events = database.execute('SELECT * FROM bookable_events', query=True)
    user_bookings = database.execute('SELECT * FROM bookings WHERE student_username=?', (username,), query = True)

    all_bookings = database.execute('SELECT * FROM bookings', (), query = True)

    existing_bookings = {}
    for booking in all_bookings:
        if booking[0] not in existing_bookings:
            existing_bookings[booking[0]] = []

        existing_bookings[booking[0]].append(booking[2])

    if request.method == 'POST':
        event_name = request.form['book_button']
        selected_time = request.form['time_slot_' + event_name]

        insert = True

        for booking in user_bookings:
            if booking[0] == event_name:
                insert = False
                error_message = 'You cannot book multiple slots for the same event.'
                break

        if insert and selected_time not in existing_bookings.get(event_name, []):
            database.execute('INSERT INTO bookings VALUES (?, ?, ?)', (event_name, username, selected_time))
            return redirect((url_for('student_dashboard')))

    return render_template('student_dashboard.html',
                           bookable_events=bookable_events,
                           user_bookings=user_bookings,
                           existing_bookings = existing_bookings,
                           error_message=error_message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect((url_for('login')))

@app.route('/reset')
def reset():
    database.execute('DROP TABLE users')
    database.execute('DROP TABLE bookable_events')
    database.execute('DROP TABLE bookings')
    return 'Reset complete'

if __name__ == '__main__':
    database.create_defaults()
    app.run(debug=True)