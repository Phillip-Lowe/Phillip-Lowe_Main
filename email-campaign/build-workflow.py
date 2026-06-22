#!/usr/bin/env python3
"""Build n8n workflow JSON from standalone template files."""

import json
import os

WORKSPACE = "/Users/philliplowe/.openclaw/workspaces/sol/email-campaign"

def load_js(filename):
    with open(os.path.join(WORKSPACE, filename), 'r') as f:
        return f.read()

# Load all template files
templates = {
    'monday': load_js('monday-item-of-week.js'),
    'tuesday': load_js('tuesday-catering.js'),
    'wednesday': load_js('wednesday-meal-prep-close.js'),
    'thursday': load_js('thursday-reopen.js'),
    'friday': load_js('friday-weekend.js'),
    'saturday': load_js('saturday-weekend.js'),
    'sunday': load_js('sunday-preview.js'),
}

workflow = {
    "name": "Utopia Deli — Weekly Email Campaign (Combined)",
    "nodes": [
        {
            "parameters": {
                "rule": {
                    "interval": [{"field": "cron", "expression": "0 9 * * *"}]
                }
            },
            "id": "trigger-schedule",
            "name": "Daily 9AM Trigger",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.1,
            "position": [0, 300]
        },
        {
            "parameters": {
                "jsCode": "// Get current day of week and week number\nconst now = new Date();\nconst days = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday'];\nconst dayOfWeek = days[now.getDay()];\n\n// Calculate week number for Tuesday rotation\nconst startOfYear = new Date(now.getFullYear(), 0, 1);\nconst weekNumber = Math.ceil(((now - startOfYear) / 86400000 + startOfYear.getDay() + 1) / 7);\n\nreturn [{\n  json: {\n    campaign_day: dayOfWeek,\n    week_number: weekNumber,\n    date: now.toISOString().split('T')[0]\n  }\n}];"
            },
            "id": "set-day",
            "name": "Set Day & Week",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [200, 300]
        },
        {
            "parameters": {
                "dataPropertyName": "campaign_day",
                "rules": {
                    "values": [
                        {"value": "monday", "output": 0},
                        {"value": "tuesday", "output": 1},
                        {"value": "wednesday", "output": 2},
                        {"value": "thursday", "output": 3},
                        {"value": "friday", "output": 4},
                        {"value": "saturday", "output": 5},
                        {"value": "sunday", "output": 6}
                    ]
                }
            },
            "id": "switch-day",
            "name": "Route by Day",
            "type": "n8n-nodes-base.switch",
            "typeVersion": 3,
            "position": [400, 300]
        },
        {
            "parameters": {"jsCode": templates['monday']},
            "id": "code-monday",
            "name": "Monday — Item of the Week",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [600, 100]
        },
        {
            "parameters": {"jsCode": templates['tuesday']},
            "id": "code-tuesday",
            "name": "Tuesday — Catering",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [600, 200]
        },
        {
            "parameters": {"jsCode": templates['wednesday']},
            "id": "code-wednesday",
            "name": "Wednesday — Meal Prep Close",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [600, 300]
        },
        {
            "parameters": {"jsCode": templates['thursday']},
            "id": "code-thursday",
            "name": "Thursday — Reopen + Deli",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [600, 400]
        },
        {
            "parameters": {"jsCode": templates['friday']},
            "id": "code-friday",
            "name": "Friday — Weekend Kickoff",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [600, 500]
        },
        {
            "parameters": {"jsCode": templates['saturday']},
            "id": "code-saturday",
            "name": "Saturday — Weekend Reminder",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [600, 600]
        },
        {
            "parameters": {"jsCode": templates['sunday']},
            "id": "code-sunday",
            "name": "Sunday — Week Preview",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [600, 700]
        },
        {
            "parameters": {
                "operation": "send",
                "subject": "={{ $json.subject }}",
                "emailType": "html",
                "message": "={{ $json.body }}",
                "toRecipients": "={{ $json.to }}"
            },
            "id": "send-email",
            "name": "Send Email (Gmail/SendGrid)",
            "type": "n8n-nodes-base.emailSend",
            "typeVersion": 2,
            "position": [800, 300]
        }
    ],
    "connections": {
        "Daily 9AM Trigger": {"main": [[{"node": "Set Day & Week", "type": "main", "index": 0}]]},
        "Set Day & Week": {"main": [[{"node": "Route by Day", "type": "main", "index": 0}]]},
        "Route by Day": {
            "main": [
                [{"node": "Monday — Item of the Week", "type": "main", "index": 0}],
                [{"node": "Tuesday — Catering", "type": "main", "index": 0}],
                [{"node": "Wednesday — Meal Prep Close", "type": "main", "index": 0}],
                [{"node": "Thursday — Reopen + Deli", "type": "main", "index": 0}],
                [{"node": "Friday — Weekend Kickoff", "type": "main", "index": 0}],
                [{"node": "Saturday — Weekend Reminder", "type": "main", "index": 0}],
                [{"node": "Sunday — Week Preview", "type": "main", "index": 0}]
            ]
        },
        "Monday — Item of the Week": {"main": [[{"node": "Send Email (Gmail/SendGrid)", "type": "main", "index": 0}]]},
        "Tuesday — Catering": {"main": [[{"node": "Send Email (Gmail/SendGrid)", "type": "main", "index": 0}]]},
        "Wednesday — Meal Prep Close": {"main": [[{"node": "Send Email (Gmail/SendGrid)", "type": "main", "index": 0}]]},
        "Thursday — Reopen + Deli": {"main": [[{"node": "Send Email (Gmail/SendGrid)", "type": "main", "index": 0}]]},
        "Friday — Weekend Kickoff": {"main": [[{"node": "Send Email (Gmail/SendGrid)", "type": "main", "index": 0}]]},
        "Saturday — Weekend Reminder": {"main": [[{"node": "Send Email (Gmail/SendGrid)", "type": "main", "index": 0}]]},
        "Sunday — Week Preview": {"main": [[{"node": "Send Email (Gmail/SendGrid)", "type": "main", "index": 0}]]}
    },
    "settings": {"executionOrder": "v1"},
    "staticData": None,
    "tags": []
}

output_path = os.path.join(WORKSPACE, "utopia-deli-weekly-email-campaign.json")
with open(output_path, 'w') as f:
    json.dump(workflow, f, indent=2)

print(f"✅ Workflow JSON written: {output_path}")
print(f"Size: {os.path.getsize(output_path):,} bytes")
