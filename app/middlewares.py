import pydantic as pyd
from functools import wraps
from typing import Any, Callable, Dict, Optional
from flask import current_app as app
from app.utils.errors import Errors as err
from skip_db_lib.models import job as job_model
from skip_db_lib.database.jobs import JobDatabase as db


def update_job_quotation(quote_func: Callable[[Any], Optional[Dict[str, Any]]]):
    """
    Validate given quotation fields and updates the incoming job in database.

    Args:
        quote_func (Callable[[Any], Optional[Dict[str, Any]]])
    """

    @wraps(quote_func)
    def update_job_quotation_wrapper(*args):
        _cls = args[0]
        job_id: str = args[1]
        quotation_fields: Dict[str, Any] = args[2]

        try:
            quotation = job_model.JobQuotation(**quotation_fields)
            job = job_model.JobUpdate(
                **{
                    "job_quotation": quotation,
                }
            )

            app.logger.debug(f"updating job {job_id} in db with quotation data")

            res = db.update_job(
                job_id, job, curr_job_status=job_model.JobStatusEnum.FREELANCER_FOUND
            )
            if not res.acknowledged:
                return err.db_op_not_acknowledged(job.dict(exclude_none=True), op="update")

            app.logger.debug(f"job {job_id} updated in db")

        except pyd.ValidationError as e:
            return err.validation_error(e, quotation_fields)
        except Exception as e:
            return err.general_exception(e)

        return quote_func(_cls, job_id, quotation)

    return update_job_quotation_wrapper


def update_job_approved(approved_func: Callable[[Any], Optional[Dict[str, Any]]]):
    """Updating a job that it is approved.

    Args:
        approved_func (Callable[[Any], Optional[Dict[str, Any]]])
    """

    @wraps(approved_func)
    def update_job_approved_wrapper(*args):
        _cls = args[0]
        job_id: str = args[1]

        try:
            job = job_model.JobUpdate(**{"job_status": job_model.JobStatusEnum.APPROVED})

            res = db.update_job(
                job_id, job, curr_job_status=job_model.JobStatusEnum.FREELANCER_FOUND
            )
            if not res.acknowledged:
                return err.db_op_not_acknowledged(job.dict(exclude_none=True), op="update")

        except pyd.ValidationError as e:
            return err.validation_error(e)
        except Exception as e:
            return err.general_exception(e)

        return approved_func(_cls, job_id)

    return update_job_approved_wrapper
