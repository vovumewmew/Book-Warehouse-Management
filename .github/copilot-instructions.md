## Project quick-guide for AI coding agents

This file gives focused, actionable guidance to help an AI agent be immediately productive in this repository (Book Warehouse Management).

### Big picture
- Purpose: a small Python app that manages books, suppliers and import/export records backed by MySQL.
- Structure:
  - `config/` — shared infrastructure (DB connection, validators, base DAO/service and base model).
  - `source/models/` — domain models (each model extends `config.basemodel.BaseModel`). Examples: `Sach.py`, `NhaPhanPhoi.py`.
  - `source/dao/` — low-level DB access classes implementing `config.basedao.BaseDAO`. Example: `SachDAO.py` contains SQL queries and returns model instances via `Model.from_dict`.
  - `source/services/` — service layer wrapping DAOs and business logic (inherits `config.baseservice.BaseService`).
  - `ui/` — UI scripts (CLI/restore utilities).
  - `main.py` — small runner demonstrating DB connectivity.

### Key patterns & conventions (copy these exactly)
- Models implement `to_dict(self) -> dict` and `@classmethod from_dict(cls, data: dict)`; DAOs call `Model.from_dict(row)` when reading from DB and pass model instances to `insert/update`.
- Soft-delete pattern: many tables use the column `TinhKhaDung` with values `"Khả dụng"` or `"Không khả dụng"`. Use this for logical deletions and filtering.
- ID formats:
  - Books: `ID_Sach` follows `S\d+` (regex used in `source/models/Sach.py`).
  - Suppliers: `ID_NguonXuat` uses `NX\d+` (see `NhaPhanPhoi.py`).
- Validators live in `config/validator.py`. Reuse these functions (`is_non_empty_string`, `is_valid_email`, `is_a_phonenumber`, `is_valid_year`) rather than reimplementing validation logic.
- DB access:
  - Use `config.db_connection.DatabaseConnection` to get `conn`. DAOs accept a `DatabaseConnection` instance and keep `self.conn = db.get_connection()`.
  - DAOs manually manage cursors and call `self.conn.commit()` / `self.conn.rollback()` on errors. Follow existing error handling and logging style.

### Files to inspect when you change behavior
- `config/db_connection.py` — contains hard-coded default DB credentials; be cautious (secrets present). For production/changes, favor environment configuration.
- `config/basemodel.py`, `config/basedao.py`, `config/baseservice.py` — base contracts to implement; mirror their signatures.
- `source/dao/SachDAO.py` — representative of SQL patterns (parameterized queries, cursor usage, dict cursors, `dictionary=True`). Use as template when creating new DAO methods.
- `source/models/*.py` — model validation patterns (properties + setters). Keep validation logic consistent.

### Developer workflows & how to run locally
- Requirements: Python 3.8+ and `mysql-connector-python` (imported as `mysql.connector` in `config/db_connection.py` and DAOs).
- DB setup: a SQL dump is available at `data/bookwarehousemanagement.sql`. Import it into a local MySQL server and ensure credentials in `config/db_connection.py` match or update the file.
- Quick run (Windows cmd):
  - Ensure virtualenv and dependency installed (example):
    ```
    python -m venv .venv
    .venv\Scripts\activate
    pip install mysql-connector-python
    ```
  - Run the small connectivity check:
    ```
    python main.py
    ```

### What agents should do when modifying code
- Preserve validators in `config/validator.py`. If you need new validations, add helpers there and update models to reuse them.
- When adding DAO methods:
  - Use parameterized queries (`%s`) and pass tuples.
  - Use `cursor(dictionary=True)` when returning rows to map easily to `Model.from_dict`.
  - Follow the commit/rollback pattern used in `SachDAO.py` and close cursors in `finally`.
- When changing model fields or DB schema, update `to_dict`/`from_dict` in the affected model and any DAO SQL that reads/writes those columns.

### Logging & errors
- Services and DAOs use Python `logging`. `config.baseservice.BaseService` configures logging. Keep log messages clear and Vietnamese language strings consistent with existing logs.

### Examples (minimal snippets agents can follow)
- Insert a new book (pattern):
  ```py
  from config.db_connection import DatabaseConnection
  from source.dao.SachDAO import SachDAO
  from source.models.Sach import Sach

  db = DatabaseConnection()
  dao = SachDAO(db)
  sach = Sach('S123','Tên','TG','TL','2020','NXB','VN',10,'Còn hàng',100000,'Khả dụng')
  dao.insert(sach)
  ```

### Missing / out-of-scope items to ask the user about
- Are you ok with the DB credentials stored in `config/db_connection.py`? Should we switch to environment variables?
- Do you want tests added (none found in repository)? If yes, indicate preferred test runner (pytest/unittest).

---
If you want I can commit this file now. Tell me if you prefer English or Vietnamese wording, and whether to add a short example for creating DAOs/services for other models.
