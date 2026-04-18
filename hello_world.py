from localflare import LocalFlare

# Personal fork - running on port 8080 to avoid conflicts with other local services
app = LocalFlare(__name__, title="Hello LocalFlare")

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>Hello LocalFlare</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f0f0f0;
                }
                .container {
                    text-align:rem;
                    -color: white;
                    0 2px 4</style>
        </head>
        <body>
            <div class="container">
                <h1>Hello LocalFlare!</h1>
                <p>Running locally on port 8080.</p>
            </div>
        </body>
    </html>
    '''

if __name__ == '__main__':
    # debug=True enables auto-reload on file changes, handy during local development
    app.run(port=8080, debug=True)
