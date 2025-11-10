from app import create_app, db
from app.utils.seed import seed_sample_data

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # create tables if not present
        db.create_all()
        # seed sample data for demo
        try:
            seed_sample_data()
        except Exception as e:
            print("Seeding failed:", e)
    app.run(host="0.0.0.0", port=5000, debug=True)
