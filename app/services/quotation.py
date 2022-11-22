import flask
import pydantic as pyd

from typing import List, Tuple
from flask import jsonify
from flask import current_app as app
from firebase_admin import messaging

from skip_common_lib.middleware import job_quotation as middlware
from skip_common_lib.utils.errors import Errors as err
from skip_common_lib.models import job as job_model
from skip_common_lib.models import customer as customer_model
from skip_common_lib.models import freelancer as freelancer_model
from skip_common_lib.database.freelancers import FreelancerDatabase as freelancers_db
from skip_common_lib.database.jobs import JobDatabase as jobs_db
from skip_common_lib.database.customers import CustomerDatabase as customers_db


class JobQuotation:
    @staticmethod
    def _exclude_failed_tokens(tokens: List[str], resps: List[messaging.SendResponse]) -> List[str]:
        """Finds the failed registration tokens in 'resps' and remove
        them from database cause they are proably invalid.

        Args:
            tokens (List[str]): Registration tokens that a notification pushed to.
            resps (List[messaging.SendResponse]): List of responses from each notification for each freelancer notified.

        Returns:
            List[str]: List of all the registration tokens that actually notified
        """
        failed_tokens = [tokens[idx] for idx, resp in enumerate(resps) if not resp.success]
        app.logger.debug(f"discarding invalid registration tokens {failed_tokens}")

        # TODO implement the call to the db function that remove the registration token from freelancers
        # implement here during testing with real registration tokens

        return [t for t in failed_tokens if t not in tokens]

    @classmethod
    @pyd.validate_arguments
    def _notify_customer(
        cls, quotation: job_model.JobQuotation, customer: customer_model.Customer
    ) -> None:
        # TODO write docstring
        app.logger.info("notifying customer about job quotation")

        msg = messaging.Message(
            data=quotation.quotation_to_str(), token=customer.registration_token
        )
        # resp = messaging.send(msg, dry_run=True)

        # app.logger.debug(f"customer notified with message {resp}")

    @classmethod
    @pyd.validate_arguments
    def _notify(
        cls, job_id: str, customer: customer_model.Customer, freelancer: freelancer_model.Freelancer
    ) -> None:
        # TODO write docstring
        app.logger.info(
            f"notifying customer {customer.email} and freelancer {freelancer.email} about job quotation approved for job {job_id}"
        )

        msg = messaging.MulticastMessage(
            data={"message": f"job {job_id} approved"},
            tokens=[customer.registration_token, freelancer.registration_token],
        )
        resp: messaging.BatchResponse = messaging.send_multicast(msg, dry_run=True)
        # TODO unfreeze here when working with real registration tokens
        # if resp.failure_count > 0:
        #     return cls._exclude_failed_tokens(
        #         [customer.registration_token, freelancer.registration_token], resp.responses
        #     )

        app.logger.debug(f"customer and freelancer are both notified")

    @classmethod
    @middlware.update_job_quotation
    def quote(cls, job_id, quotation: job_model.JobQuotation) -> Tuple[flask.Response, int]:
        """Retrieval of job by the given 'job_id',
        Retrieval of the corresponding customer and notify him about the quotation.

        Args:
            job_id (_type_): An id of a job.
            quotation (job_model.JobQuotation)

        Returns:
            Tuple[flask.Response, int]
        """
        try:
            # get corresponding job
            job = job_model.Job(**jobs_db.get_job_by_id(job_id))

            # get corresponding customer
            customer = customer_model.Customer(
                **customers_db.get_customer_by_email(job.customer_email)
            )

            cls._notify_customer(quotation, customer)

        except pyd.ValidationError as e:
            return err.validation_error(e)
        except Exception as e:
            return err.general_exception(e)

        return jsonify(message=f"notification pushed to customer {customer.email}"), 200

    @classmethod
    @middlware.update_job_approved
    def approve(cls, job_id: str) -> Tuple[flask.Response, int]:
        try:
            # get corresponding job
            job = job_model.Job(**jobs_db.get_job_by_id(job_id))

            # get corresponding customer
            customer = customer_model.Customer(
                **customers_db.get_customer_by_email(job.customer_email)
            )

            # get corresponding freelancer
            freelancer = freelancer_model.Freelancer(
                **freelancers_db.get_freelancer_by_email(job.freelancer_email)
            )

            cls._notify(job_id, customer, freelancer)

        except pyd.ValidationError as e:
            return err.validation_error(e)
        except Exception as e:
            return err.general_exception(e)

    @classmethod
    def decline() -> Tuple[flask.Response, int]:
        pass
