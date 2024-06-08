# Remove conflicting library
pip3 uninstall flask-socketio -y

# Start postgres service
service postgresql start

# Setup and populate the main database
su - postgres bash -c "psql < /home/workspace/backend/setup-trivia.sql"
su - postgres bash -c "psql trivia < /home/workspace/backend/trivia.psql"

# Setup and populate the testing database
su - postgres bash -c "psql < /home/workspace/backend/setup-test.sql"
su - postgres bash -c "psql trivia_test < /home/workspace/backend/trivia.psql"
