"""Explicit retained Rev I-L thread envelope pairs, not a blanket old-part exclusion.
The existing CAD uses major-diameter screws and minor-diameter tapped pilots.
Only these named fastener/thread pairs may overlap; all other contacts stay visible.
"""
def apply(A):
 pairs=[]
 for side in ('l','r'):
  def pair(a,b):pairs.append([side+'_'+a,side+'_'+b])
  for axis in ('flex','abduct'):
   for end in ('outer','inner'):pair(axis+'_clutch_flanged_shaft',axis+'_clutch_'+end+'_M3x8')
   for i in range(2):pair(axis+f'_clutch_mount_M3x10_{i}',axis+f'_clutch_mount_M3_nut_{i}')
   pair(axis+'_drive_split_hub',axis+'_drive_pinch_M2x10')
   for i in range(2):pair(axis+f'_drive_mount_M2x4_{i}',axis+f'_drive_mount_M2_nut_{i}')
  for i in range(2):
   pair('flex_clutch_reaction_plate',f'flex_sensor_threaded_standoff_{i}')
   pair('flex_clutch_keyed_stop_cap',f'flex_sensor_cap_set_M2x4_{i}')
   pair('flex_sensor_D_keyed_magnet_cup',f'flex_sensor_keeper_set_M2x3_{i}')
   pair(f'flex_sensor_threaded_standoff_{i}',f'flex_sensor_board_M2x6_{i}')
   pair('abduct_sensor_magnet_carrier',f'abduct_sensor_magnet_cover_M2x6_{i}')
   pair(f'abduct_sensor_nylon_spacer_{i}',f'abduct_sensor_board_M2x4_{i}')
   pair(f'abduct_sensor_nylon_spacer_{i}',f'abduct_sensor_support_M2x6_{i}')
  pair('abduct_sensor_rear_journal','abduct_sensor_journal_radial_M2x4')
  pair('abduct_sensor_rear_journal','abduct_sensor_carrier_axial_M2x6')
 names={q['name'] for q in A.parts}
 assert all(set(p)<=names for p in pairs)
 A.thread_pairs.extend(pairs)
 return pairs
