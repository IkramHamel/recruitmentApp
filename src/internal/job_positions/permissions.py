PERMISSIONS_JOBS = {
    "Job Management": {
        "description": "Allows managing jobs.",
        "permissions": [
            {"name": "create_job", "description": "Allows creating a new job."},
            {"name": "view_job", "description": "Allows listing  jobs information."},
            {"name": "update_job", "description": "Allows updating job information."},
            {"name": "delete_job", "description": "Allows deleting a job."},
            {"name": "show_job", "description": "Allows viewing job details."},
            
        ]
    }
}
PERMISSIONS_CANDIDATES = {
    "Candidate Management": {
        "description": "Allows managing Candidates.",
        "permissions": [
            {"name": "create_candidate", "description": "Allows creating a new candidate."},
            {"name": "delete_candidate", "description": "Allows deleting a candidate."},
            
        ]
    }
}
