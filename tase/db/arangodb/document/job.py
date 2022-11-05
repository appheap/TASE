from __future__ import annotations

from typing import Optional

from pydantic import Field

from .base_document import BaseDocument
from ..base.index import PersistentIndex
from ..enums import JobType


class Job(BaseDocument):
    _collection_name = "doc_jobs"
    schema_version = 1
    _extra_indexes = [
        PersistentIndex(
            version=1,
            name="is_active",
            fields=[
                "is_active",
            ],
        ),
        PersistentIndex(
            version=1,
            name="job_type",
            fields=[
                "job_type",
            ],
        ),
        PersistentIndex(
            version=1,
            name="last_run_at",
            fields=[
                "last_run_at",
            ],
        ),
    ]

    is_active: bool = Field(default=True)

    job_type: JobType
    last_run_at: int = Field(default=0)

    @classmethod
    def parse_key(
        cls,
        job_type: JobType,
    ) -> Optional[str]:
        if job_type is None or job_type == JobType.UNKNOWN:
            return None

        return f"job_{job_type.value}"

    @classmethod
    def parse(
        cls,
        job_type: JobType,
        last_run_at: int = None,
    ) -> Optional[Job]:
        key = cls.parse_key(job_type)
        if key is None:
            return None

        job = Job(
            key=key,
            job_type=job_type,
        )
        if last_run_at is not None:
            job.last_run_at = last_run_at

        return job

    def activate(self) -> bool:
        self_copy: Job = self.copy(deep=True)
        self_copy.is_active = True

        return self.update(self_copy, reserve_non_updatable_fields=False)

    def deactivate(self) -> bool:
        self_copy: Job = self.copy(deep=True)
        self_copy.is_active = False

        return self.update(self_copy, reserve_non_updatable_fields=False)

    def update_last_run(
        self,
        last_run_at: int,
    ) -> bool:
        if last_run_at is None:
            return False

        self_copy: Job = self.copy(deep=True)
        self_copy.last_run_at = last_run_at

        return self.update(self_copy, reserve_non_updatable_fields=False)


class JobMethods:
    def create_job(
        self,
        job_type: JobType,
        last_run_at: int = None,
    ) -> Optional[Job]:
        if job_type is None or job_type == JobType.UNKNOWN:
            return None

        job, successful = Job.insert(Job.parse(job_type, last_run_at))
        if job and successful:
            return job

        return None

    def get_or_create_job(
        self,
        job_type: JobType,
        last_run_at: int = None,
    ) -> Optional[Job]:
        if job_type is None or job_type == JobType.UNKNOWN:
            return None

        job = Job.get(Job.parse_key(job_type))
        if job is None:
            job = self.create_job(job_type, last_run_at)

        return job

    def get_count_interactions_job(self) -> Optional[Job]:
        return self.get_or_create_job(JobType.COUNT_INTERACTION_TYPE)

    def get_count_hits_job(self) -> Optional[Job]:
        return self.get_or_create_job(JobType.COUNT_HITS)
