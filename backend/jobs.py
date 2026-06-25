from core.job_store import (
    create_job_record,
    update_job_step_record,
    complete_job_record,
    fail_job_record,
    get_job_record
)
import uuid


def create_job():

    job_id = str(uuid.uuid4())
    create_job_record(job_id)
    return job_id


def update_job_step(job_id, step_message):

    update_job_step_record(job_id, step_message)


def complete_job(job_id, result):

    complete_job_record(job_id, result)


def fail_job(job_id, error_message):

    fail_job_record(job_id, error_message)


def get_job(job_id):

    return get_job_record(job_id)