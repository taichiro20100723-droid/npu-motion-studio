from npu_motion_studio.jobs import Job, JobStore


def test_job_store_evicts_oldest() -> None:
    store = JobStore(max_jobs=2)
    first = store.add(Job.create())
    second = store.add(Job.create())
    third = store.add(Job.create())

    assert store.get(first.id) is None
    assert store.get(second.id) is second
    assert store.get(third.id) is third
