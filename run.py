import os
from app import create_app


app = create_app(os.getenv("ENV", "development"))

if __name__ == "__main__":
    app.run(port=os.getenv("PORT", 8000), debug=os.getenv("DEBUG", True))
