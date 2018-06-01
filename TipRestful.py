from app import create_app

app = create_app()

# @app.route('/')
# def hello_world():
#     return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], port=8080, threaded=True)
    '''
    processes = 1可以调多进程
    '''
