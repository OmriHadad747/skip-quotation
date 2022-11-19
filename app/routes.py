import flask

from typing import Tuple
from flask import Blueprint
from flask import request
from app.services.quotation import JobQuotation


job_quotation_bp = Blueprint("job_quotation_bp", "job_quotation")


@job_quotation_bp.post("/quotation/<string:id>")
def post_quotation(id: str) -> Tuple[flask.Response, int]:
    return JobQuotation.quote(id, request.json)


@job_quotation_bp.post("/quotation/approve/<string:id>")
def approve_quotation(id: str) -> Tuple[flask.Response, int]:
    return JobQuotation.approve(id, request.json)


@job_quotation_bp.post("/quotation/decline/<string:id>")
def decline_quotation(id: str) -> Tuple[flask.Response, int]:
    return JobQuotation.decline(id, request.json)
