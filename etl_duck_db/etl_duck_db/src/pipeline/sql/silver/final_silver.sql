SELECT s.* FROM ({source}) s
ANTI JOIN {target} t
  ON s.event_id = t.event_id