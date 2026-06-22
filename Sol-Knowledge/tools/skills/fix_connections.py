import sqlite3, json

conn = sqlite3.connect('/Users/philliplowe/.n8n/database.sqlite')
cursor = conn.cursor()

# Get current workflow
cursor.execute("SELECT nodes, connections FROM workflow_entity WHERE id = '1WEM4rZxjhhy7ooM'")
row = cursor.fetchone()
nodes = json.loads(row[0])
conns = json.loads(row[1])

print("Before fix:")
print(f"  Log to Postgres -> {conns.get('Log to Postgres', {})}")
print(f"  Code in JavaScript -> {conns.get('Code in JavaScript', {})}")
print(f"  Send Confirmation Email -> {conns.get('Send Confirmation Email', {})}")

# Fix: Log to Postgres should go to Code in JavaScript (wait for email before responding)
# Then Code -> Send Email -> Success Response
conns['Log to Postgres'] = {
    "main": [
        [
            {
                "node": "Code in JavaScript",
                "type": "main",
                "index": 0
            }
        ]
    ]
}

# Keep: Create Payment Link -> Code in JavaScript
# Keep: Code in JavaScript -> Send Confirmation Email
# Change: Send Confirmation Email -> Success Response (already correct)

print("\nAfter fix:")
print(f"  Log to Postgres -> {conns.get('Log to Postgres', {})}")
print(f"  Code in JavaScript -> {conns.get('Code in JavaScript', {})}")
print(f"  Send Confirmation Email -> {conns.get('Send Confirmation Email', {})}")

# Update workflow
cursor.execute(
    "UPDATE workflow_entity SET connections = ? WHERE id = '1WEM4rZxjhhy7ooM'",
    (json.dumps(conns),)
)
conn.commit()
conn.close()
print("\n✅ Connections fixed")
