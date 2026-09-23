"""Post-verification exports reuse immutable CAD in one process."""
import flex_encoder as l
from functools import lru_cache
l.build=lru_cache(maxsize=2)(l.build)
import check_readout_l,export_components_l,load_budget_l,build_review_l
for stage in (check_readout_l,export_components_l,load_budget_l,build_review_l):
    stage.main()
