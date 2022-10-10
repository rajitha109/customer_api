from application import create_app

app = create_app()
# Run app
if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8080)