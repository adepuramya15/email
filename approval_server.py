from flask import Flask, request
import requests

app = Flask(__name__)

# Replace this with your actual Harness API Key
HARNESS_API_KEY = "your-harness-api-key"  # Optional: load from env
HARNESS_APPROVAL_URL_TEMPLATE = "https://app.harness.io/gateway/pipeline/api/v1/executions/{pipeline_id}/approvals/status"

headers = {
    "x-api-key": HARNESS_API_KEY,
    "Content-Type": "application/json"
}


@app.route("/approve")
def approve():
    pipeline_id = request.args.get("pipeline_id")

    print(f"✅ Received APPROVE for pipeline_id={pipeline_id}")
    
    if HARNESS_API_KEY != "your-harness-api-key":
        url = HARNESS_APPROVAL_URL_TEMPLATE.format(pipeline_id=pipeline_id)
        payload = { "approvalStatus": "APPROVED" }

        response = requests.post(url, headers=headers, json=payload)
        print("Harness response:", response.status_code, response.text)
    
    return f"""
    <h1 style='color:green;'>✅ APPROVED</h1>
    <p>Pipeline ID: {pipeline_id}</p>
    """


@app.route("/reject")
def reject():
    pipeline_id = request.args.get("pipeline_id")

    print(f"❌ Received REJECT for pipeline_id={pipeline_id}")
    
    if HARNESS_API_KEY != "your-harness-api-key":
        url = HARNESS_APPROVAL_URL_TEMPLATE.format(pipeline_id=pipeline_id)
        payload = { "approvalStatus": "REJECTED" }

        response = requests.post(url, headers=headers, json=payload)
        print("Harness response:", response.status_code, response.text)

    return f"""
    <h1 style='color:red;'>❌ REJECTED</h1>
    <p>Pipeline ID: {pipeline_id}</p>
    """


if __name__ == "__main__":
    # Must bind to 0.0.0.0 for external access (via ngrok)
    app.run(host="0.0.0.0", port=5000)
