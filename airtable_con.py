import os
from dotenv import load_dotenv
from pyairtable import Table
from datetime import datetime

load_dotenv()

# Create an instance of Table
auth_token = os.getenv("AIRTABLE_AUTH_TOKEN")
base_id = os.getenv("AIRTABLE_BASE_ID")
table_name = 'tbliQNwInhCBoK87z'
record_id = 'recN8r0ygRGFagidP'
airtable = Table(auth_token, base_id, table_name)

def get_answer():
    record = airtable.get(record_id)
    answer = record['fields']['question']
    return answer


if __name__ == "__main__":
    from app import app
    app.run(debug=True)
