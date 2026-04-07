import streamlit as st
import requests


st.set_page_config(page_title="LabFlow by JAG", layout="wide")

API_UPLOAD_URL = "http://127.0.0.1:8000/upload"
API_BASE_URL = "http://127.0.0.1:8000"


st.title("LabFlow by Jesús Garcia")
st.write("Internal tool for experiment CSV uploads, validation, processing, and results.")

st.header("Upload CSV")
uploaded_file = st.file_uploader("Choose an experiment CSV file", type="csv")

st.header("Validation Status")

if uploaded_file is None:
    st.info("Upload a CSV file to validate it.")
else:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}

    try:
        # Send the uploaded file to the FastAPI backend for validation.
        response = requests.post(API_UPLOAD_URL, files=files, timeout=30)
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.RequestException:
        st.error(
            "LabFlow could not connect to the backend. Make sure the FastAPI app is running."
        )
    else:
        if payload.get("status") == "valid":
            st.success("This CSV file passed validation.")
            if payload.get("job_id"):
                st.write(f"Job ID: `{payload['job_id']}`")
            if payload.get("job_status") == "completed":
                st.write(f"Total samples: {payload.get('total_samples')}")
                st.write(f"Positive rate: {payload.get('positive_rate'):.2%}")
            elif payload.get("job_status") == "failed":
                st.error(f"Processing failed: {payload.get('error_message')}")
        else:
            st.error("This CSV file did not pass validation.")
            for error in payload.get("errors", []):
                st.write(f"- {error}")

st.header("Check Job Status")

job_id_input = st.text_input("Enter a job ID")

if st.button("Check Status"):
    if not job_id_input.strip():
        st.error("Please enter a job ID before checking the status.")
    else:
        try:
            response = requests.get(
                f"{API_BASE_URL}/job/{job_id_input.strip()}",
                timeout=30,
            )
        except requests.exceptions.RequestException:
            st.error(
                "LabFlow could not connect to the backend. Make sure the FastAPI app is running."
            )
        else:
            if response.status_code == 404:
                st.error("No job was found for that job ID.")
            else:
                try:
                    response.raise_for_status()
                    job = response.json()
                except requests.exceptions.RequestException:
                    st.error("LabFlow returned an unexpected error while checking the job.")
                else:
                    st.subheader("Job Details")
                    st.write(f"Job ID: `{job['job_id']}`")
                    st.write(f"Status: `{job['status']}`")

                    if job["status"] == "completed":
                        st.success("This job finished successfully.")
                        st.write(f"Total samples: {job.get('total_samples')}")
                        st.write(f"Positive rate: {job.get('positive_rate', 0):.2%}")
                    elif job["status"] == "failed":
                        st.error("This job failed during processing.")
                        st.write(f"Error: {job.get('error_message')}")
