"""CLI for recording a review decision; reviewer-id must come from a trusted host."""
import argparse, json
from review_decisions import ReviewDecisionStore
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default="output/intake-workflows.sqlite")
    parser.add_argument("--workflow-id", required=True)
    parser.add_argument("--item-id", required=True)
    parser.add_argument("--reviewer-id", required=True)
    parser.add_argument("--outcome", required=True, choices=["ACCEPTED_FOR_NEXT_STAGE", "REJECTED", "REQUESTED_INFORMATION"])
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    result = ReviewDecisionStore(args.database).record(args.workflow_id, args.item_id, args.reviewer_id, args.outcome, args.reason)
    print(json.dumps(result, ensure_ascii=False, indent=2))
if __name__ == "__main__": main()
