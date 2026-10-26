# Cloud Notes — AWS CI/CD Practice Project

A separate medium-level project for learning a complete automated deployment pipeline.

## Architecture

GitHub → AWS CodePipeline → AWS CodeBuild (tests) → S3 pipeline artifact store → AWS CodeDeploy → Amazon EC2

The application is a small Flask status dashboard with `/health`, automated tests, a CodeBuild build specification, CodeDeploy AppSpec, and EC2 deployment scripts.

## Local setup (Windows PowerShell)

Run commands from the folder containing `app.py` and `requirements-dev.txt`:

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000/` and `http://127.0.0.1:5000/health`. Stop the server with Ctrl+C.

## GitHub setup

Create a new empty repository called `cloud-notes-cicd` in your own GitHub account. Do not initialize it with a README, license, or .gitignore.

```powershell
git init
git add .
git commit -m "Initial Cloud Notes CI/CD project"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/cloud-notes-cicd.git
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with your real username. If `origin` already exists, use `git remote set-url origin https://github.com/YOUR_GITHUB_USERNAME/cloud-notes-cicd.git`. Never commit AWS credentials or tokens.

## AWS build and deployment plan

1. Select one AWS region for all resources.
2. Create a GitHub connection in AWS Developer Tools and wait until its status is Available.
3. Create an EC2 Amazon Linux 2023 instance and tag it `Project=CloudNotes`.
4. Create an EC2 instance profile with the currently recommended CodeDeploy agent permissions.
5. Install and verify the CodeDeploy agent using the current AWS documentation for your region and OS.
6. Create the CodeDeploy application `cloud-notes-cicd` with compute platform EC2/On-premises, then deployment group `cloud-notes-ec2` targeting tag `Project=CloudNotes`.
7. Create CodeBuild project `cloud-notes-build`, source and artifacts type CodePipeline, managed Linux image with Python 3.12 support, `buildspec.yml`, CloudWatch logs enabled.
8. Create CodePipeline `cloud-notes-pipeline` with GitHub source (`main`), CodeBuild build stage, and CodeDeploy deploy stage.
9. The pipeline's S3 artifact store holds artifacts. You typically do not need a separate manually managed S3 bucket for a first pipeline.
10. Push a normal code change and confirm the pipeline deploys it.
11. Test a failing test in a separate commit, confirm the build fails and deployment does not proceed, then revert/fix and confirm recovery.

## IAM roles

Use separate roles and least privilege. Review current AWS docs because recommended policies can change:
- CodePipeline service role: access GitHub connection, invoke CodeBuild/CodeDeploy, access pipeline artifact bucket.
- CodeBuild role: CloudWatch Logs and required artifact access.
- CodeDeploy service role: current AWS CodeDeploy service-role policy for EC2 deployments (commonly `AWSCodeDeployRole`).
- EC2 instance profile: permissions required by the CodeDeploy agent (commonly `AmazonEC2RoleforAWSCodeDeploy`).

Do not attach AdministratorAccess for convenience, and do not put secrets in source code.

## Security and cost

- Check current AWS pricing and Free Tier eligibility before creating resources.
- Use a small eligible EC2 instance. Charges may apply for EC2, EBS, public IPv4, S3, CloudWatch logs, and pipeline/build usage.
- Restrict SSH (22) to your own IP. Restrict TCP 8000 to your IP for temporary testing; do not expose it broadly. For production use a reverse proxy/load balancer and HTTPS.
- Avoid a NAT Gateway for this simple lab unless your architecture requires it.
- Terminate EC2, delete pipeline/build/deployment resources, empty and delete the artifact bucket if no longer used, remove unused volumes/IPs/log groups/roles/connections, then review Billing.

## Troubleshooting

- GitHub source failure: verify connection is Available, repository/branch and permissions.
- Build failure: inspect CodeBuild CloudWatch logs and pytest output.
- No EC2 instances: verify deployment group tag and AWS region.
- Agent not online: verify agent service, instance profile, and outbound connectivity.
- Hook failure: inspect CodeDeploy deployment logs and `journalctl -u cloud-notes.service`.
- Health failure: run `curl http://127.0.0.1:8000/health` on EC2 and inspect `systemctl status cloud-notes.service`.

## Practice milestones

1. Local app and three tests pass.
2. Push to GitHub.
3. CodeBuild passes.
4. CodePipeline source/build stages pass.
5. CodeDeploy deploys to EC2.
6. Deliberate failing test blocks deployment; fix it and rerun successfully.
7. Clean up all lab resources.

GitHub Actions CI workflow verification.
