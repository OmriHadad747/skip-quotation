import flask

from typing import Tuple
from flask import Blueprint, request

from app.services.quotation import JobQuotation


job_quotation_bp = Blueprint("job_quotation_bp", "job_quotation")


@job_quotation_bp.post("/quotation/<string:job_id>")
def post_quotation(job_id: str) -> Tuple[flask.Response, int]:
    return JobQuotation.quote(job_id, request.json)


@job_quotation_bp.post("/quotation/approve/<string:job_id>")
def approve_quotation(job_id: str) -> Tuple[flask.Response, int]:
    return JobQuotation.approve(job_id)


@job_quotation_bp.post("/quotation/decline/<string:job_id>")
def decline_quotation(job_id: str) -> Tuple[flask.Response, int]:
    return JobQuotation.decline(job_id, request.json)
