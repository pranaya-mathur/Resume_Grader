import json


def compute_final_score(parsed_json, resume_text):

    resume_text_lower = resume_text.lower()

    try:
        content = parsed_json["choices"][0]["message"]["content"]
        data = json.loads(content)
    except:
        return 0, "Parsing Error"

    infra_stack = [x.lower() for x in data.get("infra_stack", [])]
    ml_stack = [x.lower() for x in data.get("ml_stack", [])]
    years_exp = data.get("years_experience", 0)
    has_deploy = data.get("has_production_deployment", False)
    cicd = data.get("ci_cd_used", False)
    exaggeration = data.get("exaggeration_score", 0)
    project_depth = data.get("project_depth_score", 0)

    # ------------------------------
    # 🔥 CLOUD DETECTION (Hybrid)
    # ------------------------------

    cloud_score = 0

    # LLM detection
    if any("aws" in x for x in infra_stack):
        cloud_score += 10
    if any("gcp" in x for x in infra_stack):
        cloud_score += 10
    if any("azure" in x for x in infra_stack):
        cloud_score += 8

    # Deterministic override
    if "aws" in resume_text_lower:
        cloud_score = max(cloud_score, 10)
    if "gcp" in resume_text_lower or "google cloud" in resume_text_lower:
        cloud_score = max(cloud_score, 10)
    if "azure" in resume_text_lower:
        cloud_score = max(cloud_score, 8)

    if "kubernetes" in resume_text_lower or "eks" in resume_text_lower:
        cloud_score += 5

    cloud_score = min(cloud_score, 30)

    # ------------------------------
    # 🔥 LLMPOps Maturity
    # ------------------------------

    llmops_score = 0

    if cicd or "github actions" in resume_text_lower:
        llmops_score += 5

    if "docker" in resume_text_lower:
        llmops_score += 5

    if "mlflow" in resume_text_lower or "monitor" in resume_text_lower:
        llmops_score += 5

    if project_depth >= 7:
        llmops_score += 5

    llmops_score = min(llmops_score, 20)

    # ------------------------------
    # ML Depth
    # ------------------------------

    ml_score = min(len(set(ml_stack)) * 3, 15)

    # ------------------------------
    # Experience
    # ------------------------------

    if years_exp < 1:
        experience_score = 5
    elif years_exp < 3:
        experience_score = 8
    elif years_exp < 6:
        experience_score = 12
    else:
        experience_score = 15

    # ------------------------------
    # Deployment
    # ------------------------------

    deploy_score = 10 if has_deploy or "deployed" in resume_text_lower else 0

    # ------------------------------
    # Exaggeration
    # ------------------------------

    exaggeration_penalty = exaggeration * 2

    final_score = (
        cloud_score +
        llmops_score +
        ml_score +
        experience_score +
        deploy_score
        - exaggeration_penalty
    )

    final_score = max(0, min(int(final_score), 100))

    # ------------------------------
    # Category
    # ------------------------------

    if final_score >= 80 and cloud_score >= 10:
        category = "AI System Engineer"
    elif final_score >= 65:
        category = "Deployer"
    elif final_score >= 50:
        category = "Builder"
    else:
        category = "Hobbyist"

    return final_score, category