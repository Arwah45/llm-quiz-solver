# run_solver.py — synchronous run for debugging
import time, json
from app.quiz_solver import solve_quiz_url

email = "arwah.kamdar@gmail.com"
secret = "test-secret-12345"   # must match the secret your server used earlier
url = "https://tds-llm-analysis.s-anand.net/demo"
deadline = time.time() + 3*60

res = solve_quiz_url(email, secret, url, deadline)
print(json.dumps(res, indent=2))
