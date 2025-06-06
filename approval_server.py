from flask import Flask, request

app = Flask(__name__)

@app.route("/approve")
def approve():
    pipeline_id = request.args.get("pipeline_id")
    print(f"Received APPROVE for pipeline_id={pipeline_id}")
    return f"<h2>You approved pipeline ID {pipeline_id}</h2>"

@app.route("/reject")
def reject():
    pipeline_id = request.args.get("pipeline_id")
    print(f"Received REJECT for pipeline_id={pipeline_id}")
    return f"<h2>You rejected pipeline ID {pipeline_id}</h2>"

if __name__ == "__main__":
    # Must bind to 0.0.0.0 for ngrok to reach it
    app.run(host="0.0.0.0", port=5000)
