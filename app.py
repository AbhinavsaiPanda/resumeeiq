
from flask import Flask, render_template, request, send_file
from io import BytesIO

from resume_parser import extract_resume_text
from matcher import analyze_resume

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


@app.route("/", methods=["GET", "POST"])
def index():
    error = ""
    results = None
    job_description = ""

    if request.method == "POST":
        resume = request.files.get("resume")
        job_description = request.form.get(
            "job_description", ""
        ).strip()

        if not resume or not resume.filename:
            error = "Please select your resume PDF."

        elif not resume.filename.lower().endswith(".pdf"):
            error = "Please upload a PDF file."

        elif not job_description:
            error = "Please paste the job description."

        else:
            try:
                resume_text = extract_resume_text(resume)

                if not resume_text.strip():
                    error = (
                        "No readable text found in this PDF. "
                        "Try a text-based PDF instead of a scanned PDF."
                    )
                else:
                    results = analyze_resume(
                        resume_text,
                        job_description
                    )

            except Exception:
                app.logger.exception("Resume analysis failed")
                error = (
                    "Could not analyze this resume. "
                    "Please check the PDF and try again."
                )

    return render_template(
        "index.html",
        error=error,
        results=results,
        job_description=job_description
    )


@app.route("/download-report", methods=["POST"])
def download_report():
    score = request.form.get("match_score", "0")
    matched = request.form.getlist("matched_skills")
    missing = request.form.getlist("missing_keywords")
    suggestions = request.form.getlist("suggestions")

    report_lines = [
        "RESUMEIQ - RESUME ANALYSIS REPORT",
        "=" * 38,
        "",
        f"Text similarity score: {score}%",
        "",
        "IMPORTANT",
        "This score is not a hiring probability.",
        "It measures textual similarity between the resume and job description.",
        "",
        "MATCHED SKILLS",
        "-" * 20,
    ]

    report_lines.extend(matched or ["No matched skills detected."])

    report_lines.extend([
        "",
        "KEYWORDS NOT DETECTED",
        "-" * 22,
    ])
    report_lines.extend(missing or ["No keywords from our list were missed."])

    report_lines.extend([
        "",
        "SUGGESTIONS",
        "-" * 20,
    ])
    report_lines.extend(suggestions or ["Review your resume for clarity."])

    report_lines.extend([
        "",
        "LIMITATIONS",
        "-" * 20,
        "A keyword not detected does not necessarily mean you lack that skill.",
        "The report is an aid for reviewing your resume, not a hiring decision.",
    ])

    report_bytes = BytesIO(
        "\n".join(report_lines).encode("utf-8")
    )
    report_bytes.seek(0)

    return send_file(
        report_bytes,
        mimetype="text/plain; charset=utf-8",
        as_attachment=True,
        download_name="ResumeIQ_Analysis_Report.txt"
    )


@app.errorhandler(413)
def file_too_large(error):
    return "File too large. Please upload a PDF under 5 MB.", 413


if __name__ == "__main__":
    app.run(debug=True)
