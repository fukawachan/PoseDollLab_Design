"""Review policy agreed with the user: cross-arm contacts constrain poses.
All other cross-node intersections remain structural findings; uncertain ownership
never downgrades a finding. Reservations and same-owner joins need separate audits.
"""
def independent_arm(owner):
    base=owner.split(".")[0]
    for side in ("l","r"):
        if base in (f"upperarm_{side}",f"elbow_{side}"):
            return side
    return None

def classify_hit(hit, owners):
    a,b=owners.get(hit["a"],""),owners.get(hit["b"],"")
    sa,sb=independent_arm(a),independent_arm(b)
    pose_only=sa is not None and sb is not None and sa!=sb
    return dict(hit, classification="pose_restriction" if pose_only else "structural",
                owner_a=a, owner_b=b,
                reason="opposite_independent_arms" if pose_only else "joint_adjacent_or_unresolved")

def classify_checks(record):
    owners={p["name"]:p["owner"] for p in record["parts"]}
    for check in record["motion_checks"]:
        check["hits"]=[classify_hit(h,owners) for h in check["hits"]]
        check["structural_hits"]=sum(h["classification"]=="structural" for h in check["hits"])
        check["pose_restriction_hits"]=sum(h["classification"]=="pose_restriction" for h in check["hits"])
    record["collision_policy"]="cross_arm_contact_is_pose_restriction_v1"
    return record
