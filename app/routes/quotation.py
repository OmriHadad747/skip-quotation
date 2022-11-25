import flask

from typing import Tuple
from flask import Blueprint, request

from app.services.quotation import JobQuotation


job_quotation_bp = Blueprint("job_quotation_bp", "job_quotation")


@job_quotation_bp.post("/quotation/<string:job_id>")
def post_quotation(job_id: str) -> Tuple[flask.Response, int]:
    return JobQuotation.quote(job_id, request.json)


@job_quotation_bp.post("/quotation/<string:job_id>/confirm")
def confirm_quotation(job_id: str) -> Tuple[flask.Response, int]:
    return JobQuotation.confirm(job_id, request.args.get("confirmation", False, type=bool))