import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("GovEase-Schemes")

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError

def get_all_schemes():
    items = []
    response = table.scan()
    items.extend(response["Items"])
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response["Items"])
    return items

def filter_schemes(schemes, user_profile):
    matched = []
    for s in schemes:
        score = 0
        reasons = []

        # Age check
        age = user_profile.get("age")
        if age:
            min_a = s.get("min_age")
            max_a = s.get("max_age")
            if min_a and int(age) < int(min_a):
                continue
            if max_a and int(age) > int(max_a):
                continue
            score += 1
            reasons.append("Age eligible")

        # Income check
        income = user_profile.get("annual_income")
        if income:
            max_inc = s.get("max_income")
            if max_inc and int(income) > int(max_inc):
                continue
            score += 1
            reasons.append("Income eligible")

        # Gender check
        gender = user_profile.get("gender", "").lower()
        scheme_gender = s.get("gender", "All")
        if "Female" in scheme_gender and gender == "male":
            continue
        if scheme_gender == "Female" and gender != "female":
            continue
        score += 1

        # Category check
        category = user_profile.get("category", "").upper()
        cat_res = s.get("category_reservation", "All")
        if "All" not in cat_res:
            if category and category not in cat_res.upper():
                continue
        score += 1
        reasons.append("Category eligible")

        # State check
        state = user_profile.get("state", "")
        scheme_state = s.get("elig_state", "All")
        if "All" not in scheme_state and state:
            if state.lower() not in scheme_state.lower():
                continue
        score += 1

        # Occupation check
        occupation = user_profile.get("occupation", "").lower()
        scheme_occ = s.get("occupation", "").lower()
        if occupation and scheme_occ:
            if occupation in scheme_occ or scheme_occ in ["all", "not applicable"]:
                score += 2
                reasons.append("Occupation match")

        matched.append({
            "scheme_id": s["scheme_id"],
            "name": s["name"],
            "short_name": s["short_name"],
            "category": s["category"],
            "benefits": s["benefits"],
            "description": s["description"],
            "documents_required": s.get("documents_required", []),
            "apply_url": s.get("apply_url", ""),
            "score": score,
            "match_reasons": reasons
        })

    matched.sort(key=lambda x: x["score"], reverse=True)
    return matched

def get_ai_summary(user_profile, matched_schemes):
    top_schemes = matched_schemes[:5]
    prompt = f"""You are GovEase, a helpful Indian government scheme advisor. 
A user with the following profile is looking for government schemes:
- Age: {user_profile.get('age', 'Not specified')}
- Gender: {user_profile.get('gender', 'Not specified')}
- Annual Income: Rs.{user_profile.get('annual_income', 'Not specified')}
- State: {user_profile.get('state', 'Not specified')}
- Category: {user_profile.get('category', 'Not specified')}
- Occupation: {user_profile.get('occupation', 'Not specified')}
- Education: {user_profile.get('education', 'Not specified')}

Top matching schemes:
{json.dumps([{"name": s["name"], "benefits": s["benefits"]} for s in top_schemes], indent=2, default=decimal_default)}

Give a brief, friendly 3-4 line summary in simple English about their top matches and suggest which to apply for first. Be encouraging."""

    try:
        response = bedrock.invoke_model(
            modelId="amazon.nova-lite-v1:0",
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"maxTokens": 300, "temperature": 0.7}
            }),
            contentType="application/json",
            accept="application/json"
        )
        result = json.loads(response["body"].read())
        return result["output"]["message"]["content"][0]["text"]
    except Exception as e:
        return f"Found {len(matched_schemes)} schemes matching your profile!"

def lambda_handler(event, context):
    try:
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", event)

        user_profile = body.get("user_profile", body)

        schemes = get_all_schemes()
        matched = filter_schemes(schemes, user_profile)
        summary = get_ai_summary(user_profile, matched)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({
                "total_matched": len(matched),
                "ai_summary": summary,
                "schemes": matched[:10],
                "all_schemes_count": len(schemes)
            }, default=decimal_default)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }
