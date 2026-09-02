"""Runner local: corre la misma app que se despliega en Vercel.
   python app.py   ->   http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "api"))
from index import app  # noqa: E402

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
