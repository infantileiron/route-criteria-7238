import logging
from sqlalchemy import text,inspect
from src.config.database import engine
# SQLAlchemy create_all 只建新表，不会给已存在的表加列。
# 本项目演示库由元数据直接建表、无生产迁移工具，这里做一次幂等的兼容补齐。
def ensure_schema():
 inspector=inspect(engine)
 with engine.begin() as conn:
  run_cols={c["name"] for c in inspector.get_columns("decision_runs")} if inspector.has_table("decision_runs") else set()
  if "dataset_version_id" not in run_cols:
   conn.execute(text("ALTER TABLE decision_runs ADD COLUMN dataset_version_id VARCHAR(80) DEFAULT ''"))
   logging.info("added decision_runs.dataset_version_id")
  ds_cols={c["name"] for c in inspector.get_columns("alternative_datasets")} if inspector.has_table("alternative_datasets") else set()
  if "current_version" not in ds_cols:
   conn.execute(text("ALTER TABLE alternative_datasets ADD COLUMN current_version INTEGER DEFAULT 1"))
   logging.info("added alternative_datasets.current_version")
