"""Run staged access checks with a shared immutable in-memory CAD cache."""
import flex_encoder as l
from functools import lru_cache
l.build=lru_cache(maxsize=2)(l.build)
import check_legacy_tools_l,check_twist_tools_l,check_flex_tools_l
check_legacy_tools_l.main()
check_twist_tools_l.main()
check_flex_tools_l.main()
