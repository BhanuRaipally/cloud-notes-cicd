# DevOps Status Dashboard — AWS CI/CD Practice Project

A medium-level learning project for:

**GitHub → AWS CodePipeline → AWS CodeBuild → S3 pipeline artifact → AWS CodeDeploy → Amazon EC2**

The Flask app has a homepage, `/health` endpoint, automated pytest tests, a CodeBuild buildspec, and CodeDeploy lifecycle scripts.

> Cost and account note: AWS services can incur charges. Check current pricing and your account's Free Tier eligibility before creating resources. Delete resources after practice. CodeCommit is not used; GitHub is the source repository.

## Architecture

1. Push a commit to GitHub.
2. CodePipeline detects the commit through a GitHub connection.
3. CodeBuild installs dependencies and runs `pytest`.
4. CodeBuild emits the deployable files as a pipeline artifact; CodePipeline stores/transfers artifacts using its S3 artifact store.
5. CodeDeploy deploys the artifact to EC2 and runs the lifecycle scripts.
6. The `ValidateService` hook calls `http://127.0.0.1:8000/health`.

## A. Run locally first (Windows PowerShell)

Install Python 3.11+ and Git. In PowerShell, change directory to this project:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pytest -q
python app.py
```

Open `http://127.0.0.1:5000/` and `http://127.0.0.1:5000/health`.
Stop the local server with Ctrl+C.

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` and `.\.venv\Scripts\python.exe -m pytest -q` without activating.

## B. Create GitHub repository and push

Create an empty GitHub repository named `devops-status-dashboard` (do not add a README if you already have this one). In this folder:

```bash
git init
git add .
git commit -m "Initial DevOps dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/devops-status-dashboard.git
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME`. Never commit AWS keys or tokens.

## C. Create the EC2 target

Use an Amazon Linux 2023 EC2 instance in a region you will also use for CodePipeline, CodeBuild, and CodeDeploy.

Suggested lab sizing: a small eligible instance type, subject to current account eligibility and region availability. Use a key pair only if you need SSH troubleshooting. Configure the instance security group:
- SSH (22): only your own public IP, and only if SSH is needed.
- TCP 8000: only your own IP for direct testing, or temporarily use a controlled testing method. Do not expose it to the entire internet permanently.
- Do not open broad inbound access to all ports.

Attach an EC2 instance profile with the AWS managed policy `AmazonEC2RoleforAWSCodeDeploy` (check current AWS guidance for the current recommended policy). The instance needs outbound access to download packages and communicate with CodeDeploy; avoid adding a NAT Gateway for this small public-subnet lab unless necessary.

### Install the CodeDeploy agent on EC2

Connect to the instance and run the current AWS-documented installation steps for CodeDeploy agent in your selected region and OS. On Amazon Linux, consult the AWS CodeDeploy agent installation guide for the supported package/commands for your region. Then check:

```bash
sudo systemctl status codedeploy-agent
```

If the agent isn't installed/running, deployments will fail. Follow the current AWS guide rather than copying a region-specific installer URL from an old tutorial.

## D. IAM roles — minimum required roles

Use separate roles, and grant only what each component needs. AWS-managed policy names and recommended policies can change, so review the current AWS service-role documentation before attaching permissions.

1. **CodePipeline service role**: allows CodePipeline to access the configured GitHub connection, invoke CodeBuild and CodeDeploy, and access its S3 artifact bucket.
2. **CodeBuild service role**: CloudWatch Logs write permissions and read/write access to the pipeline artifact bucket as needed by CodePipeline integration. Do not give AdministratorAccess.
3. **CodeDeploy service role**: use the current AWS CodeDeploy service-role policy for EC2 deployments (commonly `AWSCodeDeployRole`).
4. **EC2 instance profile**: allows the CodeDeploy agent on the instance to access required deployment resources (commonly `AmazonEC2RoleforAWSCodeDeploy`).
5. **GitHub connection**: create/authorize the CodeStar connection from the AWS Developer Tools console. The connection must show **Available** before pipeline use.

Avoid embedding access keys in code or buildspec. For a learning lab, prefer service roles and a GitHub connection.

## E. Create CodeDeploy application and deployment group

1. Open **AWS CodeDeploy** in your chosen region.
2. Create application: `devops-status-dashboard`.
3. Compute platform: **EC2/On-premises**.
4. Create deployment group: `devops-dashboard-ec2`.
5. Select the CodeDeploy service role.
6. Select EC2 instances using a tag, for example key `Project`, value `DevOpsDashboard`. Add that tag to the target EC2 instance.
7. Choose **CodeDeployDefault.OneAtATime** for a single-instance lab.
8. Configure deployment failure handling/rollback if available and desired.

The EC2 instance must have the CodeDeploy agent running and matching tags.

## F. Create CodeBuild project

1. Open CodeBuild → Create build project.
2. Project name: `devops-dashboard-build`.
3. Source: **CodePipeline** (CodePipeline will supply source).
4. Environment: managed Linux image that supports Python 3.12 and `buildspec.yml`; enable privileged mode only if you later add Docker builds.
5. Buildspec: use `buildspec.yml` from source.
6. Service role: select/create the CodeBuild role.
7. Artifacts: **CodePipeline**.
8. Logs: enable CloudWatch Logs.
9. Save. Do not run the pipeline yet if CodeDeploy/EC2 isn't ready.

## G. Create CodePipeline

1. Open CodePipeline → Create pipeline.
2. Name: `devops-dashboard-pipeline`.
3. Service role: select/create CodePipeline service role.
4. Artifact store: default S3 artifact store in the same region.
5. Source stage: GitHub (via **GitHub via GitHub App / CodeStar connection**), select the connection, repository, and `main` branch. Enable change detection.
6. Build stage: add CodeBuild project `devops-dashboard-build`.
7. Deploy stage: choose **AWS CodeDeploy**, application `devops-status-dashboard`, deployment group `devops-dashboard-ec2`.
8. Create pipeline and allow the first run to complete.

Pipeline artifacts are stored/transferred through the artifact store. You normally do not need to create a separate manually managed deployment bucket for this pipeline, though you may create one for learning; do not confuse it with the pipeline's artifact store.

## H. Verify deployment

When all stages succeed, browse to `http://EC2_PUBLIC_IP:8000/` (only if your security group permits your IP). Check `http://EC2_PUBLIC_IP:8000/health`.

For production, do not expose Gunicorn directly. Put a reverse proxy such as Nginx or an Application Load Balancer in front, use HTTPS, and add appropriate monitoring and access controls.

## I. Test a failed build on purpose

1. Edit `tests/test_app.py` and temporarily change an expected value to something wrong.
2. Commit and push the change.
3. Observe CodePipeline → CodeBuild. The build should fail at `pytest`; deployment should not run.
4. Revert the bad test change, commit, and push again.
5. Confirm build and deployment succeed.

## J. Troubleshooting checklist

- **Source stage fails**: verify GitHub connection is `Available`, repository/branch are correct, and pipeline role permissions are correct.
- **Build stage fails**: open CodeBuild → Build logs in CloudWatch; check Python version, requirements, and test failures.
- **Deploy stage says no instances**: confirm EC2 tag matches deployment-group filters and region is correct.
- **Agent offline**: check `systemctl status codedeploy-agent`, instance profile, outbound connectivity, and agent logs.
- **Hook fails**: inspect `/opt/codedeploy-agent/deployment-root/` logs and `journalctl -u devops-dashboard.service`.
- **Health check fails**: verify service with `sudo systemctl status devops-dashboard.service` and `curl http://127.0.0.1:8000/health`.
- **Can't reach website**: confirm the instance is running, the app listens on port 8000, and security group allows your current IP.

## K. Cleanup (important)

When finished:
1. Delete the CodePipeline pipeline.
2. Delete the CodeBuild project.
3. Delete the CodeDeploy deployment group and application.
4. Terminate the EC2 instance.
5. Delete unattached EBS volumes and unused Elastic IPs, if any.
6. Delete the S3 artifact bucket only after emptying it and confirming no other project uses it.
7. Delete unused CloudWatch log groups if you no longer need them.
8. Remove unused IAM roles/policies and the GitHub connection only if no other pipeline uses them.
9. Check Billing/Cost Explorer after cleanup.

## Suggested practice milestones

- Milestone 1: local Flask app and tests pass.
- Milestone 2: GitHub repo contains the project.
- Milestone 3: CodeBuild tests pass.
- Milestone 4: CodePipeline source/build stages pass.
- Milestone 5: CodeDeploy deploys to EC2.
- Milestone 6: a deliberate test failure stops deployment, then a fix restores the pipeline.
