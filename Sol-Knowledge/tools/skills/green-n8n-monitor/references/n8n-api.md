# n8n API Reference

## Authentication

All requests require the `X-N8N-API-KEY` header.

## Endpoints

### List Executions
```
GET /api/v1/executions?limit=50&includeData=false
```

Response:
```json
{
  "data": [
    {
      "id": "12345",
      "workflowId": "IW27pwPj5DBYQdcq",
      "status": "success",
      "startedAt": "2026-06-05T05:59:00Z",
      "stoppedAt": "2026-06-05T06:00:00Z",
      "data": {
        "resultData": {
          "error": null
        }
      }
    }
  ]
}
```

### Get Workflow
```
GET /api/v1/workflows/{id}
```

Response:
```json
{
  "id": "IW27pwPj5DBYQdcq",
  "name": "Payment Confirmed Email",
  "active": true,
  "createdAt": "2026-06-01T00:00:00Z",
  "updatedAt": "2026-06-04T00:00:00Z"
}
```

## Status Values

- `success` — Execution completed successfully
- `error` — Execution failed with error
- `crashed` — Execution crashed (node error)
- `waiting` — Execution waiting for webhook/manual trigger
- `running` — Execution currently running

## Error Handling

Errors are in `execution.data.resultData.error`:
```json
{
  "message": "Connection refused",
  "description": "Unable to connect to the server",
  "context": {}
}
```
