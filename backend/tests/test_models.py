from app.core.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

def test_job_areas_exist():
    assert hasattr(JobArea, "TI_SOFTWARE")
    assert hasattr(JobArea, "DADOS")
    assert hasattr(JobArea, "DESIGN")
    assert JobArea.TI_SOFTWARE.value == "TI_SOFTWARE"

def test_job_modalities_exist():
    assert hasattr(JobModality, "REMOTE")
    assert hasattr(JobModality, "HYBRID")
    assert hasattr(JobModality, "ONSITE")
    assert JobModality.REMOTE.value == "REMOTE"

def test_job_statuses_exist():
    assert hasattr(JobStatus, "ACTIVE")
    assert hasattr(JobStatus, "CLOSED")

def test_source_statuses_exist():
    assert hasattr(SourceStatus, "ACTIVE")
    assert hasattr(SourceStatus, "INACTIVE")
    assert hasattr(SourceStatus, "ERROR")
