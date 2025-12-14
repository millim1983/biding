**Dev Container**

- **Prerequisites:** Install Docker Desktop and VS Code.
- **Open locally:** In VS Code run: `Remote-Containers: Reopen in Container` (or click the green >< icon).
- **Open in Codespaces:** In GitHub UI: `Code → Codespaces → Create` and choose the repository/branch.

**Ports exposed (dev):**
- FastAPI: `8000`
- Postgres: `5432`

**DB (development) connection info**
- host (from inside containers): `db`
- host (from host when forwarded): `localhost:5432`
- user/password/db: `postgres` / `postgres` / `postgres`

**Start locally (optional)**
Run the compose stack (this will create the DB and an app container that sleeps):

```bash
docker compose up -d
```

Then open a terminal in the `app` container (or Reopen in Container) and install/run your app.

Example FastAPI run (inside the `app` container):

```bash
# if you use requirements.txt
pip install -r requirements.txt
# or if your pyproject supports editable install
pip install -e .
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Notes / Security**
- Do NOT hardcode secrets or API keys in source. Use `.env` and keep `.env` ignored.
- If files are already committed, `.gitignore` does not remove them. To stop tracking an already committed file run:

```bash
git rm --cached <file>
```

