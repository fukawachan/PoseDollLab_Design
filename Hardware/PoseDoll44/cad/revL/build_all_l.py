"""Complete Rev L digital build with one immutable CAD cache."""
import flex_encoder as l
from functools import lru_cache
l.build=lru_cache(maxsize=2)(l.build)
import verify_l,check_legacy_tools_l,check_twist_tools_l,check_flex_tools_l
import check_readout_l,export_components_l,load_budget_l,build_review_l
for stage in (verify_l,check_legacy_tools_l,check_twist_tools_l,check_flex_tools_l,check_readout_l,export_components_l,load_budget_l,build_review_l):
    print('Stage: '+stage.__name__,flush=True)
    stage.main()
