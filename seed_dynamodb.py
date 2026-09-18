import json
import boto3

TABLE_NAME = "GovEase-Schemes"
REGION = "us-east-1"

def seed():
    with open("govease_schemes.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    schemes = data["schemes"]
    print(f"Found {len(schemes)} schemes to upload...")

    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)

    success = 0
    errors = 0

    with table.batch_writer() as batch:
        for scheme in schemes:
            try:
                item = {
                    "scheme_id": scheme["scheme_id"],
                    "name": scheme["name"],
                    "short_name": scheme["short_name"],
                    "category": scheme["category"],
                    "description": scheme["description"],
                    "benefits": scheme["benefits"],
                    "documents_required": scheme["documents_required"],
                    "apply_url": scheme["apply_url"],
                    "is_central": scheme["is_central"],
                    "state": scheme["state"],
                    "min_age": scheme["eligibility"].get("min_age"),
                    "max_age": scheme["eligibility"].get("max_age"),
                    "max_income": scheme["eligibility"].get("max_income"),
                    "education_level": scheme["eligibility"].get("education_level"),
                    "gender": scheme["eligibility"].get("gender"),
                    "category_reservation": scheme["eligibility"].get("category_reservation"),
                    "elig_state": scheme["eligibility"].get("state"),
                    "occupation": scheme["eligibility"].get("occupation"),
                    "other_criteria": scheme["eligibility"].get("other_criteria"),
                }
                item = {k: v for k, v in item.items() if v is not None}
                batch.put_item(Item=item)
                success += 1
                print(f"  OK {scheme['scheme_id']}: {scheme['short_name']}")
            except Exception as e:
                errors += 1
                print(f"  FAIL {scheme['scheme_id']}: {e}")

    print(f"\nDone! {success} uploaded, {errors} errors")

if __name__ == "__main__":
    seed()
